import pandas as pd

excel_file = '/home/ubuntu/upload/930E-5-PlanodeManutençãoPreventiva-15.07.2025.xlsx'
df = pd.read_excel(excel_file)

# Salvar as primeiras 20 linhas do DataFrame em um arquivo de texto para análise
with open('/home/ubuntu/excel_content_preview.txt', 'w') as f:
    f.write(df.head(20).to_string())

print('Conteúdo do Excel salvo em excel_content_preview.txt')

