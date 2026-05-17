#!/usr/bin/env python
"""
TempoBERT 快速演示脚本
使用极少数据快速展示TempoBERT的核心功能
"""

import os
import sys
import torch
from pathlib import Path
from datetime import datetime

from loguru import logger

# 导入兼容模块
from tempobert_compat import (
    TempoBertTokenizer,
    DataCollatorForTempoBERT,
    load_temporal_dataset,
    prepare_dataset_for_training,
    predict_time,
    compute_semantic_change_score,
    find_time_from_filename,
)
from transformers import BertForMaskedLM, Trainer, TrainingArguments

# 设置日志
logger.remove()
logger.add(sys.stderr, level="INFO")


def quick_demo():
    """快速演示TempoBERT的核心功能"""
    
    logger.info("=" * 60)
    logger.info("TempoBERT 快速演示")
    logger.info("=" * 60)
    
    data_path = Path("datasets")
    output_dir = Path("output") / f"quick_demo_{datetime.now().strftime('%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 选择2个时间点进行快速演示
    selected_times = ["1990", "2020"]
    
    logger.info(f"\n[步骤1] 加载数据 (时间点: {selected_times})")
    
    # 手动加载少量数据
    all_texts = []
    all_times = []
    max_per_time = 500  # 每个时间点只取500条
    
    for time in selected_times:
        txt_file = data_path / f"nyt_{time}.txt"
        if txt_file.exists():
            with open(txt_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()][:max_per_time]
                all_texts.extend(lines)
                all_times.extend([time] * len(lines))
    
    logger.info(f"加载了 {len(all_texts)} 条文本")
    
    # 创建数据集
    import datasets
    train_dataset = datasets.Dataset.from_dict({
        "text": all_texts,
        "time": all_times
    })
    
    logger.info("\n[步骤2] 加载模型和tokenizer")
    
    # 加载tokenizer
    tokenizer = TempoBertTokenizer.from_pretrained_with_times(
        "bert-base-uncased",
        times=selected_times
    )
    
    # 加载模型
    model = BertForMaskedLM.from_pretrained("bert-base-uncased")
    model.resize_token_embeddings(len(tokenizer))
    
    logger.info(f"词汇表大小: {len(tokenizer)}")
    logger.info(f"时间token: {[f'<{t}>' for t in selected_times]}")
    
    logger.info("\n[步骤3] 预处理数据")
    
    # tokenize
    def tokenize_function(examples):
        texts_with_time = [
            f"<{t}> {text}" 
            for text, t in zip(examples["text"], examples["time"])
        ]
        return tokenizer(
            texts_with_time,
            truncation=True,
            max_length=64,
            padding="max_length",
            return_special_tokens_mask=True
        )
    
    tokenized_dataset = train_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=train_dataset.column_names,
        desc="Tokenizing"
    )
    
    logger.info(f"处理后数据集大小: {len(tokenized_dataset)}")
    
    logger.info("\n[步骤4] 训练模型 (快速: 50步)")
    
    # 数据整理器
    time_tokens = [f"<{t}>" for t in selected_times]
    data_collator = DataCollatorForTempoBERT(
        tokenizer=tokenizer,
        mlm_probability=0.15,
        time_mlm_probability=0.5,
        time_tokens=time_tokens
    )
    
    # 训练参数 - 极简配置
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=1,
        per_device_train_batch_size=16,
        max_steps=50,  # 只训练50步
        logging_steps=10,
        save_steps=100,
        learning_rate=5e-5,
        warmup_steps=5,
        report_to="none",
        use_cpu=not torch.backends.mps.is_available(),  # 使用MPS或CPU
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        processing_class=tokenizer,
    )
    
    # 训练
    start_time = datetime.now()
    trainer.train()
    train_time = datetime.now() - start_time
    
    logger.info(f"训练完成! 耗时: {train_time}")
    
    # 保存模型
    trainer.save_model()
    tokenizer.save_pretrained(str(output_dir))
    
    # 保存times配置
    import json
    config_path = output_dir / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    config["times"] = selected_times
    config["time_embedding_type"] = "prepend_token"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"模型已保存到: {output_dir}")
    
    logger.info("\n[步骤5] 时间预测演示")
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model.to(device)
    tokenizer.times = selected_times
    
    test_sentences = [
        "The Soviet Union announced new policies today.",
        "Scientists are studying the coronavirus pandemic.",
        "The economy is growing rapidly this year.",
    ]
    
    for sentence in test_sentences:
        probs = predict_time(model, tokenizer, sentence, device)
        logger.info(f"\n句子: {sentence}")
        logger.info("预测概率:")
        for time_token, prob in probs.items():
            logger.info(f"  {time_token}: {prob:.4f}")
    
    logger.info("\n[步骤6] 语义变化检测演示")
    
    # 构建测试数据
    test_word = "technology"
    time_sentences = {}
    
    from textsearch import TextSearch
    ts = TextSearch(case="ignore", returns="match")
    ts.add([test_word])
    
    for time in selected_times:
        txt_file = data_path / f"nyt_{time}.txt"
        sentences = []
        if txt_file.exists():
            with open(txt_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ts.findall(line) and len(sentences) < 30:
                        sentences.append(line)
        time_sentences[time] = sentences
        logger.info(f"  {time}: 找到 {len(sentences)} 个包含 '{test_word}' 的句子")
    
    if all(len(s) > 0 for s in time_sentences.values()):
        score = compute_semantic_change_score(
            model, tokenizer, test_word, time_sentences, device
        )
        logger.info(f"\n词 '{test_word}' 的语义变化分数: {score:.4f}")
        logger.info("(分数越高表示语义变化越大)")
    else:
        logger.warning(f"某些时间点缺少包含 '{test_word}' 的句子")
    
    logger.info("\n" + "=" * 60)
    logger.info("快速演示完成!")
    logger.info("=" * 60)
    
    return output_dir


if __name__ == "__main__":
    quick_demo()
