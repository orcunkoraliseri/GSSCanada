import torch
import numpy as np

def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence between two distributions."""
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))

def compute_floor():
    print("Loading data...")
    train_data = torch.load(r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\outputs_step4\step4_train.pt', map_location='cpu')
    pairs = torch.load(r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\outputs_step4\training_pairs.pt', map_location='cpu')
    
    act_seq = train_data['act_seq'].numpy()  # (N, 48)
    tgt_k_indices = pairs['tgt_k_indices'].numpy()  # (n_pairs, 5)
    
    n_pairs = len(tgt_k_indices)
    print(f"Loaded {n_pairs} training pairs with K=5 neighbors each.")
    
    total_js = 0.0
    valid_pairs = 0
    
    print("Computing pairwise neighbor disagreement...")
    # To speed this up, let's pre-compute the distributions for all respondents
    # distributions: (N, 14)
    print("Pre-computing marginals for all respondents...")
    distributions = np.zeros((len(act_seq), 14), dtype=np.float32)
    for i in range(len(act_seq)):
        dist = np.bincount(act_seq[i], minlength=14).astype(np.float32)
        distributions[i] = dist / (dist.sum() + 1e-12)

    # Now compute pairwise JS for the 5 neighbors
    all_js_vals = []
    
    # We have 10 combinations of pairs from 5 items: (0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)
    pairs_idx = [(i, j) for i in range(5) for j in range(i+1, 5)]
    
    for i in range(n_pairs):
        neighbors = tgt_k_indices[i] # array of 5 indices
        
        # calculate pairwise JS between these 5 neighbors
        sum_js = 0.0
        for idx1, idx2 in pairs_idx:
            n1 = neighbors[idx1]
            n2 = neighbors[idx2]
            p = distributions[n1]
            q = distributions[n2]
            sum_js += js_divergence(p, q)
            
        avg_js = sum_js / 10.0
        all_js_vals.append(avg_js)
        
        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1}/{n_pairs}...")
            
    overall_mean = np.mean(all_js_vals)
    print(f"==================================================")
    print(f"Neighbor-Disagreement JS Floor: {overall_mean:.4f}")
    print(f"==================================================")
    
if __name__ == "__main__":
    compute_floor()
