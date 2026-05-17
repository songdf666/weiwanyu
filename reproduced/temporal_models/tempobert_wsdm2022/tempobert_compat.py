"""
TempoBERT兼容性模块 - 适配新版本transformers (4.x)
此模块提供TempoBERT的简化实现，核心功能包括：
1. 时间token嵌入
2. 时间掩码语言模型训练
3. 语义变化检测
"""

import re
import torch
import numpy as np
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from transformers import (
    BertTokenizerFast,
    BertForMaskedLM,
    BertConfig,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from transformers.tokenization_utils_base import BatchEncoding
import datasets
from loguru import logger


# ============ 配置类 ============
class TempoBertConfig(BertConfig):
    """TempoBERT配置类"""
    model_type = "tempobert"
    
    def __init__(self, times=None, time_embedding_type="prepend_token", **kwargs):
        super().__init__(**kwargs)
        self.times = times or []
        self.time_embedding_type = time_embedding_type


# ============ Tokenizer ============
class TempoBertTokenizer(BertTokenizerFast):
    """
    TempoBERT Tokenizer - 支持时间token
    在文本前添加时间标记 <year>
    """
    
    def __init__(self, *args, times=None, time_embedding_type="prepend_token", **kwargs):
        super().__init__(*args, **kwargs)
        self.times = times or []
        self.time_embedding_type = time_embedding_type
        
        # 添加时间token到词汇表
        if self.times:
            time_tokens = [f"<{t}>" for t in self.times]
            self.add_tokens(time_tokens, special_tokens=True)
    
    def encode_with_time(self, text: str, time: str, **kwargs) -> Dict[str, Any]:
        """对文本进行编码，在前面添加时间token"""
        if self.time_embedding_type == "prepend_token":
            time_token = f"<{time}>"
            text_with_time = f"{time_token} {text}"
        else:
            text_with_time = text
        
        return self(text_with_time, **kwargs)
    
    def batch_encode_with_time(
        self, 
        texts: List[str], 
        times: List[str],
        **kwargs
    ) -> BatchEncoding:
        """批量编码文本和时间"""
        if self.time_embedding_type == "prepend_token":
            texts_with_time = [f"<{t}> {text}" for text, t in zip(texts, times)]
        else:
            texts_with_time = texts
        
        return self(texts_with_time, **kwargs)
    
    @classmethod
    def from_pretrained_with_times(cls, pretrained_model_name_or_path, times, **kwargs):
        """从预训练模型加载并添加时间token"""
        tokenizer = cls.from_pretrained(pretrained_model_name_or_path, **kwargs)
        tokenizer.times = times
        tokenizer.time_embedding_type = kwargs.get("time_embedding_type", "prepend_token")
        
        # 添加时间token
        time_tokens = [f"<{t}>" for t in times]
        tokenizer.add_tokens(time_tokens, special_tokens=True)
        
        return tokenizer


# ============ Data Collator ============
class DataCollatorForTempoBERT(DataCollatorForLanguageModeling):
    """
    TempoBERT的数据整理器
    支持对时间token的特殊掩码处理
    """
    
    def __init__(
        self, 
        tokenizer, 
        mlm_probability=0.15,
        time_mlm_probability=None,
        time_tokens=None,
        **kwargs
    ):
        super().__init__(tokenizer=tokenizer, mlm=True, mlm_probability=mlm_probability, **kwargs)
        self.time_mlm_probability = time_mlm_probability or mlm_probability
        self.time_tokens = time_tokens or []
        self.time_token_ids = [tokenizer.convert_tokens_to_ids(t) for t in self.time_tokens]
    
    def torch_mask_tokens(self, inputs, special_tokens_mask=None):
        """
        对输入进行掩码，时间token使用特殊的掩码概率
        """
        labels = inputs.clone()
        
        # 创建概率矩阵
        probability_matrix = torch.full(labels.shape, self.mlm_probability)
        
        # 如果有特殊token掩码，设置其概率为0
        if special_tokens_mask is not None:
            special_tokens_mask = special_tokens_mask.bool()
            probability_matrix.masked_fill_(special_tokens_mask, value=0.0)
        
        # 对时间token使用不同的掩码概率
        if self.time_token_ids and self.time_mlm_probability != self.mlm_probability:
            for time_id in self.time_token_ids:
                time_mask = inputs == time_id
                probability_matrix.masked_fill_(time_mask, value=self.time_mlm_probability)
        
        # 生成掩码
        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = -100  # 只计算被掩码位置的loss
        
        # 80%的时间替换为[MASK]
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)
        
        # 10%的时间替换为随机token
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]
        
        # 剩余10%保持不变
        return inputs, labels


# ============ 数据集处理 ============
def find_time_from_filename(filename: str) -> Optional[str]:
    """从文件名中提取时间信息"""
    filename = Path(filename).name
    m = re.match(r".*?_(\d+.*?)[\.a-zA-Z]", filename)
    if m is None:
        return None
    time = m.group(1).strip("_")
    return time


def load_temporal_dataset(data_path: str, times: List[str] = None) -> datasets.Dataset:
    """
    加载带时间信息的文本数据集
    
    Args:
        data_path: 数据目录路径
        times: 时间点列表（如果为None则从文件名自动检测）
    
    Returns:
        包含text和time列的Dataset
    """
    data_path = Path(data_path)
    all_texts = []
    all_times = []
    
    txt_files = sorted(data_path.glob("*.txt"))
    
    for txt_file in txt_files:
        time = find_time_from_filename(str(txt_file))
        if time is None:
            continue
        if times is not None and time not in times:
            continue
            
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    all_texts.append(line)
                    all_times.append(time)
    
    logger.info(f"加载了 {len(all_texts)} 条文本，时间范围: {sorted(set(all_times))}")
    
    return datasets.Dataset.from_dict({
        "text": all_texts,
        "time": all_times
    })


def prepare_dataset_for_training(
    dataset: datasets.Dataset,
    tokenizer: TempoBertTokenizer,
    max_length: int = 128
) -> datasets.Dataset:
    """
    预处理数据集用于训练
    """
    def tokenize_function(examples):
        # 在文本前添加时间token
        texts_with_time = [
            f"<{t}> {text}" 
            for text, t in zip(examples["text"], examples["time"])
        ]
        
        result = tokenizer(
            texts_with_time,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_special_tokens_mask=True
        )
        return result
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing dataset"
    )
    
    return tokenized_dataset


# ============ 模型训练 ============
def train_tempobert(
    train_data_path: str,
    output_dir: str,
    base_model: str = "bert-base-uncased",
    times: List[str] = None,
    max_length: int = 128,
    num_epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 5e-5,
    mlm_probability: float = 0.15,
    time_mlm_probability: float = None,
    eval_data_path: str = None,
    **kwargs
):
    """
    训练TempoBERT模型
    
    Args:
        train_data_path: 训练数据路径
        output_dir: 输出目录
        base_model: 基础BERT模型
        times: 时间点列表
        max_length: 最大序列长度
        num_epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        mlm_probability: MLM掩码概率
        time_mlm_probability: 时间token掩码概率
        eval_data_path: 验证数据路径
    """
    # 加载数据集
    logger.info("加载训练数据...")
    train_dataset = load_temporal_dataset(train_data_path, times)
    
    # 自动检测时间点
    if times is None:
        times = sorted(set(train_dataset["time"]))
    logger.info(f"时间点: {times}")
    
    # 加载tokenizer并添加时间token
    logger.info(f"加载tokenizer: {base_model}")
    tokenizer = TempoBertTokenizer.from_pretrained_with_times(
        base_model, 
        times=times,
        time_embedding_type="prepend_token"
    )
    
    # 加载模型
    logger.info(f"加载模型: {base_model}")
    model = BertForMaskedLM.from_pretrained(base_model)
    
    # 调整词嵌入大小以适应新token
    model.resize_token_embeddings(len(tokenizer))
    
    # 预处理数据集
    logger.info("预处理训练数据...")
    train_tokenized = prepare_dataset_for_training(train_dataset, tokenizer, max_length)
    
    eval_tokenized = None
    if eval_data_path:
        logger.info("加载验证数据...")
        eval_dataset = load_temporal_dataset(eval_data_path, times)
        eval_tokenized = prepare_dataset_for_training(eval_dataset, tokenizer, max_length)
    
    # 数据整理器
    time_tokens = [f"<{t}>" for t in times]
    data_collator = DataCollatorForTempoBERT(
        tokenizer=tokenizer,
        mlm_probability=mlm_probability,
        time_mlm_probability=time_mlm_probability,
        time_tokens=time_tokens
    )
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_ratio=0.1,
        logging_dir=f"{output_dir}/logs",
        logging_steps=100,
        save_steps=1000,
        save_total_limit=2,
        eval_strategy="epoch" if eval_tokenized else "no",
        load_best_model_at_end=True if eval_tokenized else False,
        report_to="none",
        **kwargs
    )
    
    # 训练器
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=eval_tokenized,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # 开始训练
    logger.info("开始训练...")
    start_time = datetime.now()
    trainer.train()
    logger.info(f"训练完成! 耗时: {datetime.now() - start_time}")
    
    # 保存模型
    trainer.save_model()
    
    # 保存配置（包含times信息）
    config = TempoBertConfig(
        times=times,
        time_embedding_type="prepend_token",
        **model.config.to_dict()
    )
    config.save_pretrained(output_dir)
    
    logger.info(f"模型已保存到: {output_dir}")
    return trainer


# ============ 时间预测 ============
def predict_time(
    model,
    tokenizer: TempoBertTokenizer,
    text: str,
    device: str = "cpu"
) -> Dict[str, float]:
    """
    预测句子的时间
    
    Args:
        model: TempoBERT模型
        tokenizer: tokenizer
        text: 输入文本
        device: 设备
    
    Returns:
        时间token到概率的映射
    """
    # 在文本前添加[MASK]
    masked_text = f"{tokenizer.mask_token} {text}"
    
    inputs = tokenizer(masked_text, return_tensors="pt", truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取[MASK]位置的logits
    mask_token_index = (inputs["input_ids"] == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
    mask_logits = outputs.logits[0, mask_token_index, :].squeeze()
    
    # 获取时间token的概率
    time_probs = {}
    time_tokens = [f"<{t}>" for t in tokenizer.times]
    time_token_ids = tokenizer.convert_tokens_to_ids(time_tokens)
    
    probs = torch.softmax(mask_logits, dim=-1)
    for token, token_id in zip(time_tokens, time_token_ids):
        time_probs[token] = probs[token_id].item()
    
    # 排序
    time_probs = dict(sorted(time_probs.items(), key=lambda x: x[1], reverse=True))
    
    return time_probs


# ============ 语义变化检测 ============
def get_word_embedding(
    model,
    tokenizer: TempoBertTokenizer,
    sentences: List[str],
    word: str,
    time: str = None,
    device: str = "cpu",
    batch_size: int = 32
) -> torch.Tensor:
    """
    获取词在上下文中的嵌入表示
    
    Args:
        model: BERT模型
        tokenizer: tokenizer
        sentences: 包含目标词的句子列表
        word: 目标词
        time: 时间点（可选）
        device: 设备
        batch_size: 批次大小
    
    Returns:
        词嵌入张量
    """
    model.eval()
    model.to(device)
    
    all_embeddings = []
    
    for i in range(0, len(sentences), batch_size):
        batch_sentences = sentences[i:i+batch_size]
        
        # 如果指定时间，添加时间token
        if time and hasattr(tokenizer, 'times'):
            batch_sentences = [f"<{time}> {s}" for s in batch_sentences]
        
        inputs = tokenizer(
            batch_sentences,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
        
        # 使用最后一层隐藏状态
        hidden_states = outputs.hidden_states[-1]
        
        # 找到目标词的位置并获取嵌入
        for j, sentence in enumerate(batch_sentences):
            # 获取词的token ids
            word_ids = tokenizer.encode(word, add_special_tokens=False)
            input_ids = inputs["input_ids"][j].tolist()
            
            # 查找词在输入中的位置
            for k in range(len(input_ids) - len(word_ids) + 1):
                if input_ids[k:k+len(word_ids)] == word_ids:
                    # 获取词的平均嵌入
                    word_embedding = hidden_states[j, k:k+len(word_ids), :].mean(dim=0)
                    all_embeddings.append(word_embedding)
                    break
    
    if not all_embeddings:
        return torch.tensor([])
    
    return torch.stack(all_embeddings)


def compute_semantic_change_score(
    model,
    tokenizer: TempoBertTokenizer,
    word: str,
    time_sentences: Dict[str, List[str]],
    device: str = "cpu"
) -> float:
    """
    计算词的语义变化分数
    
    使用余弦距离衡量不同时间点的词嵌入差异
    
    Args:
        model: BERT模型
        tokenizer: tokenizer
        word: 目标词
        time_sentences: 时间点到句子列表的映射
        device: 设备
    
    Returns:
        语义变化分数
    """
    embeddings_by_time = {}
    
    for time, sentences in time_sentences.items():
        if not sentences:
            continue
        
        embs = get_word_embedding(model, tokenizer, sentences, word, time=time, device=device)
        if embs.numel() > 0:
            # 计算该时间点的平均嵌入
            embeddings_by_time[time] = embs.mean(dim=0)
    
    if len(embeddings_by_time) < 2:
        return 0.0
    
    # 计算第一个和最后一个时间点嵌入的余弦距离
    times = sorted(embeddings_by_time.keys())
    first_emb = embeddings_by_time[times[0]]
    last_emb = embeddings_by_time[times[-1]]
    
    # 余弦距离 = 1 - 余弦相似度
    cos_sim = torch.nn.functional.cosine_similarity(
        first_emb.unsqueeze(0), 
        last_emb.unsqueeze(0)
    )
    change_score = 1 - cos_sim.item()
    
    return change_score


# ============ 句子时间预测评估 ============
def evaluate_time_prediction(
    model,
    tokenizer: TempoBertTokenizer,
    test_data_path: str,
    device: str = "cpu"
) -> Dict[str, float]:
    """
    评估句子时间预测任务
    
    Args:
        model: TempoBERT模型
        tokenizer: tokenizer
        test_data_path: 测试数据路径
        device: 设备
    
    Returns:
        评估指标字典
    """
    from sklearn.metrics import accuracy_score, f1_score
    
    test_dataset = load_temporal_dataset(test_data_path, times=tokenizer.times)
    
    y_true = []
    y_pred = []
    
    time_to_label = {t: i for i, t in enumerate(sorted(tokenizer.times))}
    
    model.to(device)
    model.eval()
    
    for i, example in enumerate(test_dataset):
        true_time = example["time"]
        text = example["text"]
        
        # 预测时间
        probs = predict_time(model, tokenizer, text, device)
        pred_time = list(probs.keys())[0].strip("<>")
        
        y_true.append(time_to_label.get(true_time, -1))
        y_pred.append(time_to_label.get(pred_time, -1))
        
        if (i + 1) % 100 == 0:
            logger.info(f"已处理 {i+1}/{len(test_dataset)} 样本")
    
    # 计算指标
    accuracy = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro")
    
    results = {
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "num_samples": len(y_true)
    }
    
    logger.info(f"时间预测评估结果: Accuracy={accuracy:.4f}, Macro-F1={f1_macro:.4f}")
    
    return results


if __name__ == "__main__":
    # 示例用法
    print("TempoBERT兼容模块加载成功!")
    print("使用 train_tempobert() 函数进行训练")
    print("使用 predict_time() 函数进行时间预测")
    print("使用 compute_semantic_change_score() 函数计算语义变化")
