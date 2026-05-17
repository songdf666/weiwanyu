# Semantic Change Discovery
This repository contains code &amp; data from the paper "Semantic Change Quantification Methods Struggle with Discovery in the Wild" published at EMNLP 2025. \[[paper](https://aclanthology.org/2025.emnlp-main.1791)\] \[[poster](https://github.com/khonzoda/semantic-change-discovery-emnlp2025/blob/main/misc/poster.jpg)\] \[[slides](https://github.com/khonzoda/semantic-change-discovery-emnlp2025/blob/main/misc/slides.pdf)\]



## Getting Started: requirements 
This code uses the following libraries/packages:
  - pytorch==2.5.1
  - pytorch-cuda=11.8
  - conda-forge::transformers
  - spacy
  - scipy
  - conda-forge::jupyterlab
  - ipywidgets
  - conda-forge::evaluate
  - accelerate
  - scikit-learn
  - pydantic=2.10.2
  - conda-forge::openpyxl
  - plotly
  - pot
  - conda-forge::nltk
  
More details (dependencies & package versions) can be found under `environment.yml`. 

```
conda env create -f environment.yml
cd code
```

## Step 0: Download Raw Data (externally)

### SemEval-EN

`mkdir -p data/semeval_en/raw/`

Download and move [SemEval-EN data](https://www.ims.uni-stuttgart.de/en/research/resources/corpora/sem-eval-ulscd-eng/) to `data/semeval_en/raw/`. Unzip each `corpus1/<lemma or token>/ccoha1.txt.gz` and `corpus2/<lemma or token>/ccoha2.txt.gz`.

```
cd code
python prepare_semevalen_dataset.py
```

### LiverpoolFC

`mkdir -p data/LiverpoolFC/raw/`

Download and move [LiverpoolFC data](https://github.com/marcodel13/Short-term-meaning-shift/tree/master/Dataset) to `data/LiverpoolFC/raw/`. Unzip `LiverpoolFC_13.txt.zip` and `LiverpoolFC_17.txt.zip`.

```
cd code
python prepare_liverpoolfc_dataset.py
```

## Step 1: Process data

First, **process the raw data**: 

```
python process_data.py 	--dataset <dataset_name>\
						--infile <raw_data_infile>\
						--tokenizer-model <model_name>\
						--lemmatize\
						--pos-tag
```

For LiverpoolFC, use `LiverpoolFC` and `../data/LiverpoolFC/clean/all.jsonlist` as `<dataset_name>` and `<raw_data_infile>`, respectively. For SemEval-EN use `semeval_en` and `../data/semeval_en/merged/all.jsonlist` as `<dataset_name>` and `<raw_data_infile>`, respectively. 

For models we use `bert-base-uncased`, `bert-base-multilingual-uncased`, `FacebookAI/xlm-roberta-base`, and `pierluigic/xl-lexeme`.

Next, **map tokens to lemmas** and **compute word stats**: 

```
python match_tokens_to_lemmas.py --dataset <dataset_name>\
								 --tokenizer-model <model_name>

python compute_word_stats.py --dataset <dataset_name>\
							 --tokenizer-model <model_name>
```

From here, **sample control terms** for the given dataset's targets:
```
python sample_control_terms.py 	--dataset <dataset_name>\
								--tokenizer-model <model_name>\
								--control-terms-fname 'controls.json'
```

Finally, **index occurrences** of target and control terms of the dataset:
```
python index_term_occurrences.py 	--dataset <dataset_name>\
									--tokenizer-model <model_name>\
									--control-terms-fname 'controls.json'\
									--control-outfile 'control_indices.json'
```

## Step 2: Fine-tune the language model

After, preparing training and validation data, fine-tune the model on one of the datasets. As before, the datasets are `LiverpoolFC` and `semeval_en`; and models are `bert-base-uncased`, `bert-base-multilingual-uncased`, `FacebookAI/xlm-roberta-base`, and `pierluigic/xl-lexeme` .

```
python prepare_fine_tuning_data.py 	--dataset <dataset_name>\
									--model <model_name>

python run_fine_tuning.py 	--dataset <dataset_name>\
							--model <model_name>
```

## Step 3: Extract model embeddings

Extract model embeddings for target and control terms provided their occurrence indices:

```
python get_contextualized_embeddings.py --dataset <dataset_name>\
										--model <model_name>\
										--term-indices-fname 'target_indices.json'\
										--outdir 'target_embeddings'\
										--batch-size 32

python get_contextualized_embeddings.py --dataset <dataset_name>\
										--model <model_name>\
										--term-indices-fname 'control_indices.json'\
										--outdir 'control_embeddings'\
										--batch-size 32
```

## Step 4: Extract MLM substitute representations

Extract MLM substitutes for target and control terms provided their occurrence indices:

```
python get_mlm_substitutes.py --dataset <dataset_name>\
							  --model <model_name>\
							  --term-indices-fname 'target_indices.json'\
							  --outdir 'target_substitutes'\
							  --batch-size 32\
							  --top-k 10

python get_mlm_substitutes.py --dataset <dataset_name>\
							  --model <model_name>\
							  --term-indices-fname 'control_indices.json'\
							  --outdir 'control_substitutes'\
							  --batch-size 32\
							  --top-k 10
```

## Step 5: Compute semantic change based on sense clusters

Compute semantic change based on sense clusters following Montariol et al. (2021):
```
python get_raw_clustr_change.py --dataset <dataset_name>\
								--model <model_name>
```

## Step 6: Compute semantic change as APD between embeddings

Compute semantic change as average-pairwise-distance (APD) between embeddings

```
python get_raw_change_emb_apd.py --dataset <dataset_name>\
								 --model <model_name>
```

Embeddings (APD) semantic change scores are recorded to `../results/semantic_change_scores/<dataset_name>__<model_name>__avg_pairwise_dist_by_term.json`.

## Step 7: Run permutation tests 

Run permutation tests for embeddings-based (PRT & APD) and substitutes-based (JSD) semantic change quantification methods. 

```
python run_permutations_emb_prt.py --dataset <dataset_name>\
								   --model <model_name>

python run_permutations_emb_apd.py --dataset <dataset_name>\
								   --model <model_name>

python run_permutations_subst_jsd.py --dataset <dataset_name>\
									 --model <model_name>

```

Permutation results are saved under `../results/permutations/<dataset_name>__<model_name>__<method>_permutation_pvals.json`, where `<method>` is either `emb_prt`, `emb_apd`, or `subst_jsd`.

## Step 8: Aggregate semantic change scores

Compute and aggregate semantic change scores across 
 - all methods:
 	- embeddings-based (PRT & APD), 
 	- sense-clusters-based (AP & K5),  
 	- substitutes-based (JSD)
 - and secondary techniques:
 	- frequency scaling (FS)
 	- frequency scaling with part-of-speech matching (FS_PM)
 	- permutation tests (PT)
 	- permutation tests with false-discovery rate control (PT_FDR).

```
python quantify_semantic_change.py --dataset <dataset_name>\
								   --model <model_name>
```
The aggregated semantic change scores would be written to `../results/semantic_change_scores/<dataset_name>__<model_name>__raw_scores_by_method.json`.

## Step 9: Evaluate discovery

Evaluate discovery using the ranking-based approach. 

```
python evaluate_discovery.py --dataset <dataset_name>\
							 --model <model_name>\
							 --do-discovery-base\
							 --do-discovery-FS\
							 --do-discovery-FS-PM\
							 --do-discovery-PT\
							 --do-discovery-PT-FDR
```

Rankings results are recorded under `../results/rankings/` for each dataset, model, and method + technique. In filtered rankings, only terms that have `ADJ`, `NOUN`, or `VERB` as their primary part-of-speech are kept. 
