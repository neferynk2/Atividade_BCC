import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage

def empty_lattice_bcc():
    print("Iniciando cálculos...")

    points = {
        'Γ': np.array([0., 0., 0.]),
        'H': np.array([1., 0., 0.]),
        'P': np.array([0.5, 0.5, 0.5]),
        'N': np.array([0.5, 0.5, 0.])
    }
    
    path_labels = ['Γ', 'H', 'P', 'Γ', 'N']
    path_vectors = [points[label] for label in path_labels]
    
    m_range = range(-2, 3)
    G_vectors = []
    G_labels = []
    band_indices = []
    
    count = 1
    for m1 in m_range:
        for m2 in m_range:
            for m3 in m_range:
                G_vectors.append(np.array([m1, m2, m3]))
                G_labels.append([count, m1, m2, m3])
                band_indices.append(count)
                count += 1
    
    res = 50 
    
    plot_k_path = []
    plot_energies = [] 
    excel_segments = {} 
    
    current_dist = 0
    tick_locs = [0]
    tick_labels = [path_labels[0]]
    
    for i in range(len(path_vectors) - 1):
        start_label = path_labels[i]
        end_label = path_labels[i+1]
        start_pt = path_vectors[i]
        end_pt = path_vectors[i+1]
        
        segment_name = f"{start_label}-{end_label}"
        segment_dist = np.linalg.norm(end_pt - start_pt)
        
        local_alphas = np.linspace(0, 1, res)
        local_energies = []
        
        for alpha in local_alphas:
            k_point = start_pt + alpha * (end_pt - start_pt)
            k_dist_global = current_dist + alpha * segment_dist
            plot_k_path.append(k_dist_global)
            
            energies_k = []
            for G in G_vectors:
                k_total = k_point + G
                energy = np.dot(k_total, k_total)
                energies_k.append(energy)
            
            plot_energies.append(energies_k)
            local_energies.append(energies_k)
        
        excel_segments[segment_name] = {
            'alphas': local_alphas,
            'energies': np.array(local_energies)
        }
        
        current_dist += segment_dist
        tick_locs.append(current_dist)
        tick_labels.append(end_label)

    plot_energies = np.array(plot_energies)
    
    print("Gerando gráfico...")
    fig, ax = plt.subplots(figsize=(10, 8))
    
    max_plot_energy = 5.0
    num_bands = plot_energies.shape[1]
    
    for b in range(num_bands):
        energy_curve = plot_energies[:, b]
        if np.min(energy_curve) <= max_plot_energy:
            ax.plot(plot_k_path, energy_curve, color='blue', linewidth=1.5, alpha=0.7)

    ax.set_ylim(0, 5)
    ax.set_xlim(0, max(plot_k_path))
    ax.set_ylabel(r'Energia Reduzida $\varepsilon$', fontsize=12)
    ax.set_title('Estrutura de Bandas BCC (Rede Vazia)', fontsize=14)
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labels, fontsize=12)
    for loc in tick_locs:
        ax.axvline(x=loc, color='black', linestyle='--', linewidth=0.8)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    png_filename = 'bandas_bcc_atividade.png'
    plt.tight_layout()
    plt.savefig(png_filename)
    print(f"Gráfico salvo em: {os.path.abspath(png_filename)}")

    print("Gerando planilha Excel com gráfico...")
    excel_filename = 'bandas_bcc_dados.xlsx'
    
    try:
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for seg_name, data in excel_segments.items():
                df_meta = pd.DataFrame(G_labels, columns=['Banda', 'm1', 'm2', 'm3'])
                
                alphas = data['alphas']
                energies = data['energies'] 
                
                data_dict = {'α': alphas}
                for i, band_idx in enumerate(band_indices):
                    data_dict[band_idx] = energies[:, i]
                
                df_data = pd.DataFrame(data_dict)
                
                df_meta.to_excel(writer, sheet_name=seg_name, startrow=0, index=False)
                start_row_data = len(df_meta) + 2
                df_data.to_excel(writer, sheet_name=seg_name, startrow=start_row_data, index=False)
            
            wb = writer.book
            ws_graph = wb.create_sheet("Gráfico")
            
            img = ExcelImage(png_filename)
            ws_graph.add_image(img, 'A1')
            
        print(f"Planilha salva em: {os.path.abspath(excel_filename)}")
        
    except Exception as e:
        print(f"Erro ao salvar Excel: {e}")

if __name__ == "__main__":
    empty_lattice_bcc()
