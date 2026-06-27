import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage
 
 
def empty_lattice_bcc():
    print("Iniciando calculos...")
 
    points = {
        'G': np.array([0., 0., 0.]),
        'H': np.array([1., 0., 0.]),
        'P': np.array([0.5, 0.5, 0.5]),
        'N': np.array([0.5, 0.5, 0.]),
    }
    path = ['G', 'H', 'P', 'G', 'N']
 
    
    B = np.array([[0., 1., 1.],
                  [1., 0., 1.],
                  [1., 1., 0.]])
 
    G_tables = {
        'G-H': [(0, 0, 0), (0, -1, 0), (1, 0, 0), (1, -1, -1),
                (0, 1, 0), (0, -1, -1), (1, 1, -1), (-1, 1, 1)],
        'H-P': [(0, 0, 0), (-1, 0, 0), (1, 0, 0), (1, -1, -1),
                (0, 1, 0), (0, -1, -1), (-1, -1, 0), (2, -1, -1), (-2, 0, 0)],
        'P-G': [(0, 0, 0), (0, -1, 0), (-2, 0, 1), (1, -1, -1),
                (0, 1, 0), (0, -1, -1), (1, 1, -1), (1, -1, 0), (-2, 0, 0)],
        'G-N': [(0, 0, 0), (0, -1, 0), (1, 0, 0), (1, -1, -1),
                (0, 0, 1), (0, -1, -1), (1, 1, -1), (-1, 1, 1),
                (1, -1, 0), (0, 0, -1), (-1, -1, 0), (0, 0, -2)],
    }
    disp = {'G': r'$\Gamma$', 'H': 'H', 'P': 'P', 'N': 'N'}
 
    res = 200
    fig, ax = plt.subplots(figsize=(11, 8))
 
    ticks = list(range(len(path)))
    tick_labels = [disp[p] for p in path]
    excel_segments = {}
 
    for i in range(len(path) - 1):
        a, b_pt = points[path[i]], points[path[i + 1]]
        seg = path[i] + '-' + path[i + 1]
        hkl = np.array(G_tables[seg], dtype=float)
        G = hkl @ B
 
        alphas = np.linspace(0, 1, res)
        x_seg = i + alphas
        energies = np.zeros((res, len(G)))
        for j, al in enumerate(alphas):
            k = a + al * (b_pt - a)
            energies[j, :] = np.sum((k + G) ** 2, axis=1)
 
        Nb = len(G)
        for bnd in range(Nb):
            yb = energies[:, bnd]
            ax.plot(x_seg, yb, color='blue', linewidth=1.4, alpha=0.85)
            frac = (bnd + 0.5) / Nb
            idx = int(frac * (res - 1))
            if yb[idx] > 4.8:
                idx = int(np.argmin(yb))
            if yb[idx] <= 5.0:
                ax.text(x_seg[idx], yb[idx], str(bnd + 1), fontsize=7.5,
                        color='darkblue', ha='center', va='center', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.8))
 
        excel_segments[seg] = {'G_list': G_tables[seg], 'alphas': alphas, 'energies': energies}
 
    ax.set_ylim(0, 5)
    ax.set_xlim(0, len(path) - 1)
    ax.set_ylabel(r'Energia Reduzida  $\varepsilon\,/\,[(\hbar^2/2m)(2\pi/a)^2]$', fontsize=12)
    ax.set_title('Estrutura de Bandas BCC (Rede Vazia)', fontsize=14)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, fontsize=13)
    for loc in ticks[1:-1]:
        ax.axvline(x=loc, color='black', linestyle='--', linewidth=0.8)
    ax.grid(True, axis='y', linestyle=':', alpha=0.6)
 
    png = 'bandas_bcc_atividade.png'
    plt.tight_layout()
    plt.savefig(png, dpi=120)
    print("Grafico salvo em: " + os.path.abspath(png))
 
    print("Gerando planilha Excel com grafico...")
    xlsx = 'bandas_bcc_dados.xlsx'
    try:
        with pd.ExcelWriter(xlsx, engine='openpyxl') as writer:
            for seg, data in excel_segments.items():
                meta = [[idx + 1, h, k, l] for idx, (h, k, l) in enumerate(data['G_list'])]
                df_meta = pd.DataFrame(meta, columns=['Banda', 'h', 'k', 'l'])
                data_dict = {'alpha': data['alphas']}
                for bnd in range(len(data['G_list'])):
                    data_dict['Banda ' + str(bnd + 1)] = data['energies'][:, bnd]
                df_data = pd.DataFrame(data_dict)
                df_meta.to_excel(writer, sheet_name=seg, startrow=0, index=False)
                df_data.to_excel(writer, sheet_name=seg, startrow=len(df_meta) + 2, index=False)
            ws = writer.book.create_sheet("Grafico")
            ws.add_image(ExcelImage(png), 'A1')
        print("Planilha salva em: " + os.path.abspath(xlsx))
    except Exception as e:
        print("Erro ao salvar Excel: " + str(e))
 
 
if __name__ == "__main__":
    empty_lattice_bcc()
