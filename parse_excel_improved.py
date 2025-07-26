import pandas as pd
import json

excel_file = '/home/ubuntu/upload/930E-5-PlanodeManutençãoPreventiva-15.07.2025.xlsx'

# Carregar todas as abas do Excel
xls = pd.ExcelFile(excel_file)

checklists = {}

print('\n--- Iniciando processamento do Excel por abas ---')

for sheet_name in xls.sheet_names:
    print(f'\nProcessando aba: {sheet_name}')
    df = xls.parse(sheet_name, header=None)
    
    current_category = sheet_name.strip() # A aba é a categoria
    current_periodicity = 'Não Definida'

    for index, row in df.iterrows():
        row_str = ' '.join(row.dropna().astype(str).tolist())
        
        # Identificar Periodicidade
        # Procura por 'Cada XXXH' em qualquer coluna da linha
        for cell in row.dropna().astype(str):
            if 'Cada' in cell and 'H' in cell:
                current_periodicity = cell.strip()
                break

        # Identificar Itens do Checklist
        # Assume que os itens do checklist começam com um código como A.01, B.01, etc.
        # Verifica se a primeira coluna (row[0]) é uma string, tem mais de 1 caractere,
        # contém um ponto e o primeiro caractere é uma letra.
        if isinstance(row[0], str) and len(row[0]) > 1 and '.' in row[0] and row[0][0].isalpha():
            item_code = row[0]
            item_periodicity = row[1] if pd.notna(row[1]) else ''
            item_description = row[2] if pd.notna(row[2]) else ''
            item_observation = row[6] if len(row) > 6 and pd.notna(row[6]) else ''

            if current_category not in checklists:
                checklists[current_category] = {}
            if current_periodicity not in checklists[current_category]:
                checklists[current_category][current_periodicity] = []

            checklists[current_category][current_periodicity].append({
                'code': item_code,
                'periodicity': item_periodicity,
                'description': item_description,
                'observation': item_observation
            })
            # print(f"  Item adicionado: {item_code} em {current_category}/{current_periodicity}")

print('\n--- Processamento concluído ---')
# Salvar a estrutura dos checklists em um arquivo JSON para fácil acesso
with open("checklists_structure.json", "w", encoding="utf-8") as f:
    json.dump(checklists, f, ensure_ascii=False, indent=4)

print("Estrutura dos checklists salva em checklists_structure.json")
print(f"Categorias encontradas: {list(checklists.keys())}")
for cat, periods in checklists.items():
    print(f"{cat}: {list(periods.keys())}")

