import argparse
import torch
import os
from models.Preprocess import Model

from data_provider.data_loader import Dataset_Patch_Preprocess
from torch.utils.data import DataLoader
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AutoTimes Preprocess')
    parser.add_argument('--gpu', type=int, default=0, help='gpu id')
    parser.add_argument('--llm_model', type=str, default='GPT2', help='LLM model')  # GPT2, Qwen-0.5B, Deepseek, LLAMA
    parser.add_argument('--llm_ckp_dir', type=str, default='./LLM/gpt2', help='llm checkpoints dir')
    parser.add_argument('--dataset', type=str, default='ETTh1',
                        help='dataset to preprocess, options:[ETTh1, ETTh2, ETTm1, ETTm2, electricity, weather, traffic, custom]')
    parser.add_argument('--root_path', type=str, default=None, help='root path of data file')
    parser.add_argument('--data_path', type=str, default=None, help='data file name')
    parser.add_argument('--seq_len', type=int, default=672, help='input sequence length used in prompt generation')
    parser.add_argument('--label_len', type=int, default=576, help='label length used in prompt generation')
    parser.add_argument('--pred_len', type=int, default=96, help='prediction length used in prompt generation')
    parser.add_argument('--batch_size', type=int, default=32, help='preprocess batch size')
    parser.add_argument('--num_workers', type=int, default=0, help='dataloader workers')
    args = parser.parse_args()
    print(args.dataset)

    model = Model(args)

    seq_len = args.seq_len
    label_len = args.label_len
    pred_len = args.pred_len

    assert args.dataset in ['ETTh1', 'ETTh2', 'ETTm1', 'ETTm2', 'electricity', 'weather', 'traffic', 'custom']
    default_paths = {
        'ETTh1': ('./dataset/ETT-small/', 'ETTh1.csv'),
        'ETTh2': ('./dataset/ETT-small/', 'ETTh2.csv'),
        'ETTm1': ('./dataset/ETT-small/', 'ETTm1.csv'),
        'ETTm2': ('./dataset/ETT-small/', 'ETTm2.csv'),
        'electricity': ('./dataset/electricity/', 'electricity.csv'),
        'weather': ('./dataset/weather/', 'weather.csv'),
        'traffic': ('./dataset/traffic/', 'traffic.csv'),
    }

    if args.dataset == 'custom':
        if args.root_path is None or args.data_path is None:
            raise ValueError('--dataset custom requires both --root_path and --data_path')
        root_path = args.root_path
        data_path = args.data_path
    else:
        default_root, default_file = default_paths[args.dataset]
        root_path = args.root_path if args.root_path is not None else default_root
        data_path = args.data_path if args.data_path is not None else default_file

    data_set = Dataset_Patch_Preprocess(
        root_path=root_path,
        data_path=data_path,
        size=[seq_len, label_len, pred_len],
    )

    data_loader = DataLoader(
        data_set,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )


    print(len(data_set.data_stamp))
    print(data_set.tot_len)
    save_dir_path = root_path
    data_name = os.path.splitext(os.path.basename(data_path))[0]
    output_list = []
    for idx, data in tqdm(enumerate(data_loader), total=len(data_loader), desc='Prompt Embedding'):
        # print(data)
        output = model(data)
        output_list.append(output.detach().cpu())

    result = torch.cat(output_list, dim=0)
    print(result.shape)

    save_path = os.path.join(save_dir_path, f'{data_name}_{args.llm_model}.pt')
    torch.save(result, save_path)
    print(f'Result saved to: {save_path}')
