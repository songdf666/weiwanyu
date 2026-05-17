#!/usr/bin/env python
"""
TempoBERT 动态演化建模实验脚本

本脚本实现了论文《TempoBERT: Temporal Language Models for Predicting Distant Historical Dates》
的核心功能，包括：
1. TempoBERT模型训练
2. 句子时间预测
3. 语义变化检测

使用方法:
    python run_experiment.py --mode train --data_path datasets --output_dir output
    python run_experiment.py --mode predict --model_path output/tempobert
    python run_experiment.py --mode semantic_change --model_path output/tempobert
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

import torch
from loguru import logger

# 导入兼容模块
from tempobert_compat import (
    train_tempobert,
    predict_time,
    compute_semantic_change_score,
    evaluate_time_prediction,
    load_temporal_dataset,
    TempoBertTokenizer,
    find_time_from_filename,
)
from transformers import BertForMaskedLM


def setup_logger(log_dir: str = None):
    """设置日志"""
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logger.add(log_file, level="DEBUG")


def train_mode(args):
    """训练模式"""
    logger.info("=" * 50)
    logger.info("TempoBERT 训练模式")
    logger.info("=" * 50)
    
    # 获取数据路径
    data_path = Path(args.data_path)
    
    # 自动检测时间点（从文件名）
    txt_files = list(data_path.glob("*.txt"))
    times = sorted(set(find_time_from_filename(str(f)) for f in txt_files if find_time_from_filename(str(f))))
    
    if not times:
        logger.error(f"在 {data_path} 中未找到有效的时间标记文件")
        return
    
    # 如果指定了时间范围
    if args.time_start and args.time_end:
        times = [t for t in times if args.time_start <= t <= args.time_end]
    
    # 限制时间点数量（用于快速演示）
    if args.max_times and len(times) > args.max_times:
        # 均匀采样
        step = len(times) // args.max_times
        times = times[::step][:args.max_times]
    
    logger.info(f"使用 {len(times)} 个时间点: {times}")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 开始训练
    trainer = train_tempobert(
        train_data_path=str(data_path),
        output_dir=str(output_dir),
        base_model=args.base_model,
        times=times,
        max_length=args.max_length,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        mlm_probability=args.mlm_probability,
        time_mlm_probability=args.time_mlm_probability,
    )
    
    logger.info(f"训练完成! 模型已保存到: {output_dir}")
    
    return trainer


def predict_mode(args):
    """时间预测模式"""
    logger.info("=" * 50)
    logger.info("TempoBERT 时间预测模式")
    logger.info("=" * 50)
    
    # 加载模型
    model_path = args.model_path
    logger.info(f"加载模型: {model_path}")
    
    model = BertForMaskedLM.from_pretrained(model_path)
    tokenizer = TempoBertTokenizer.from_pretrained(model_path)
    
    # 从config中读取times
    import json
    config_path = Path(model_path) / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    tokenizer.times = config.get("times", [])
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    # 示例句子
    test_sentences = [
        "The economy is growing rapidly.",
        "New technology is changing our lives.",
        "The president gave a speech yesterday.",
        "Scientists discovered a new species.",
        "The stock market crashed today.",
    ]
    
    if args.input_text:
        test_sentences = [args.input_text]
    
    logger.info("\n时间预测结果:")
    logger.info("-" * 50)
    
    for sentence in test_sentences:
        probs = predict_time(model, tokenizer, sentence, device)
        logger.info(f"\n句子: {sentence}")
        logger.info("预测时间概率:")
        for time_token, prob in list(probs.items())[:5]:
            logger.info(f"  {time_token}: {prob:.4f}")


def semantic_change_mode(args):
    """语义变化检测模式"""
    logger.info("=" * 50)
    logger.info("TempoBERT 语义变化检测模式")
    logger.info("=" * 50)
    
    # 加载模型
    model_path = args.model_path
    logger.info(f"加载模型: {model_path}")
    
    model = BertForMaskedLM.from_pretrained(model_path)
    tokenizer = TempoBertTokenizer.from_pretrained(model_path)
    
    # 从config中读取times
    import json
    config_path = Path(model_path) / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    tokenizer.times = config.get("times", [])
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    # 加载测试数据
    data_path = Path(args.data_path)
    
    # 测试词列表（可以根据需要修改）
    test_words = args.test_words.split(",") if args.test_words else [
        "virus", "phone", "network", "cloud", "tweet", "stream"
    ]
    
    logger.info(f"测试词: {test_words}")
    
    # 构建每个词在不同时间的句子集合
    from collections import defaultdict
    from textsearch import TextSearch
    
    word_time_sentences = defaultdict(lambda: defaultdict(list))
    
    txt_files = list(data_path.glob("*.txt"))
    
    for txt_file in txt_files:
        time = find_time_from_filename(str(txt_file))
        if time is None or time not in tokenizer.times:
            continue
        
        ts = TextSearch(case="ignore", returns="match")
        ts.add(test_words)
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                found_words = ts.findall(line)
                for word in found_words:
                    if len(word_time_sentences[word][time]) < args.max_sentences:
                        word_time_sentences[word][time].append(line)
    
    # 计算语义变化分数
    logger.info("\n语义变化检测结果:")
    logger.info("-" * 50)
    
    results = []
    for word in test_words:
        time_sentences = word_time_sentences[word]
        if len(time_sentences) < 2:
            logger.warning(f"词 '{word}' 的数据不足，跳过")
            continue
        
        score = compute_semantic_change_score(
            model, tokenizer, word, dict(time_sentences), device
        )
        results.append((word, score))
        logger.info(f"  {word}: {score:.4f}")
    
    # 按分数排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    logger.info("\n语义变化排名 (从高到低):")
    for i, (word, score) in enumerate(results, 1):
        logger.info(f"  {i}. {word}: {score:.4f}")


def demo_mode(args):
    """演示模式 - 快速运行整个流程"""
    logger.info("=" * 50)
    logger.info("TempoBERT 演示模式")
    logger.info("=" * 50)
    
    data_path = Path(args.data_path)
    output_dir = Path(args.output_dir) / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 1. 使用少量数据和时间点进行快速训练
    logger.info("\n[步骤1] 训练TempoBERT模型 (演示配置)")
    
    # 获取所有时间点并选择几个代表性的
    txt_files = list(data_path.glob("*.txt"))
    all_times = sorted(set(find_time_from_filename(str(f)) for f in txt_files if find_time_from_filename(str(f))))
    
    # 选择4个时间点用于演示
    if len(all_times) >= 4:
        selected_times = [all_times[0], all_times[len(all_times)//3], all_times[2*len(all_times)//3], all_times[-1]]
    else:
        selected_times = all_times
    
    logger.info(f"选择的时间点: {selected_times}")
    
    trainer = train_tempobert(
        train_data_path=str(data_path),
        output_dir=str(output_dir),
        base_model=args.base_model,
        times=selected_times,
        max_length=64,  # 较短序列加速训练
        num_epochs=1,   # 演示只训练1轮
        batch_size=8,
        learning_rate=5e-5,
        mlm_probability=0.15,
        time_mlm_probability=0.5,  # 时间token更高的掩码率
    )
    
    # 2. 时间预测演示
    logger.info("\n[步骤2] 时间预测演示")
    
    model = trainer.model
    tokenizer = trainer.tokenizer
    tokenizer.times = selected_times
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    test_sentences = [
        "The economy is growing rapidly.",
        "New technology is changing the world.",
        "The president announced new policies.",
    ]
    
    for sentence in test_sentences:
        probs = predict_time(model, tokenizer, sentence, device)
        logger.info(f"\n句子: {sentence}")
        logger.info("预测时间概率:")
        for time_token, prob in list(probs.items())[:3]:
            logger.info(f"  {time_token}: {prob:.4f}")
    
    # 3. 语义变化检测演示
    logger.info("\n[步骤3] 语义变化检测演示")
    
    test_words = ["technology", "network", "economy"]
    
    from collections import defaultdict
    from textsearch import TextSearch
    
    word_time_sentences = defaultdict(lambda: defaultdict(list))
    
    for txt_file in txt_files:
        time = find_time_from_filename(str(txt_file))
        if time is None or time not in selected_times:
            continue
        
        ts = TextSearch(case="ignore", returns="match")
        ts.add(test_words)
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                found_words = ts.findall(line)
                for word in found_words:
                    if len(word_time_sentences[word][time]) < 50:
                        word_time_sentences[word][time].append(line)
    
    logger.info("\n语义变化分数:")
    for word in test_words:
        time_sentences = word_time_sentences[word]
        if len(time_sentences) >= 2:
            score = compute_semantic_change_score(
                model, tokenizer, word, dict(time_sentences), device
            )
            logger.info(f"  {word}: {score:.4f}")
        else:
            logger.info(f"  {word}: 数据不足")
    
    logger.info("\n" + "=" * 50)
    logger.info("演示完成!")
    logger.info(f"模型已保存到: {output_dir}")
    logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="TempoBERT 动态演化建模实验",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 通用参数
    parser.add_argument("--mode", type=str, default="demo",
                       choices=["train", "predict", "semantic_change", "demo"],
                       help="运行模式: train/predict/semantic_change/demo")
    parser.add_argument("--data_path", type=str, default="datasets",
                       help="数据路径")
    parser.add_argument("--output_dir", type=str, default="output",
                       help="输出目录")
    parser.add_argument("--model_path", type=str, default=None,
                       help="模型路径(用于predict和semantic_change模式)")
    parser.add_argument("--log_dir", type=str, default="logs",
                       help="日志目录")
    
    # 训练参数
    parser.add_argument("--base_model", type=str, default="bert-base-uncased",
                       help="基础BERT模型")
    parser.add_argument("--max_length", type=int, default=128,
                       help="最大序列长度")
    parser.add_argument("--num_epochs", type=int, default=3,
                       help="训练轮数")
    parser.add_argument("--batch_size", type=int, default=16,
                       help="批次大小")
    parser.add_argument("--learning_rate", type=float, default=5e-5,
                       help="学习率")
    parser.add_argument("--mlm_probability", type=float, default=0.15,
                       help="MLM掩码概率")
    parser.add_argument("--time_mlm_probability", type=float, default=None,
                       help="时间token掩码概率")
    parser.add_argument("--time_start", type=str, default=None,
                       help="起始时间")
    parser.add_argument("--time_end", type=str, default=None,
                       help="结束时间")
    parser.add_argument("--max_times", type=int, default=None,
                       help="最大时间点数量")
    
    # 预测参数
    parser.add_argument("--input_text", type=str, default=None,
                       help="输入文本(用于predict模式)")
    
    # 语义变化参数
    parser.add_argument("--test_words", type=str, default=None,
                       help="测试词列表,逗号分隔")
    parser.add_argument("--max_sentences", type=int, default=100,
                       help="每个词每个时间点最大句子数")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logger(args.log_dir)
    
    logger.info("TempoBERT 动态演化建模实验")
    logger.info(f"运行模式: {args.mode}")
    logger.info(f"参数: {args}")
    
    # 根据模式运行
    if args.mode == "train":
        train_mode(args)
    elif args.mode == "predict":
        if not args.model_path:
            logger.error("predict模式需要指定--model_path")
            return
        predict_mode(args)
    elif args.mode == "semantic_change":
        if not args.model_path:
            logger.error("semantic_change模式需要指定--model_path")
            return
        semantic_change_mode(args)
    elif args.mode == "demo":
        demo_mode(args)


if __name__ == "__main__":
    main()
