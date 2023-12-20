import datetime

from docx import Document
import pandas as pd
from unidecode import unidecode
import re


def extract_weights2(description):
    # Dictionnaire pour stocker les poids
    weights = {'>750 mil': '', '750 mil': '', '585 mil': '', '375 mil': ''}

    # Extraire toutes les parties de la description contenant des informations de poids
    weight_parts = re.findall(r"(superieur a 750 mil|750 mil|585 mil|375 mil) = (\d+\.?\d*) g", description)

    # Parcourir les parties extraites et attribuer les poids aux catégories correspondantes
    for part in weight_parts:
        category, weight = part
        if category == 'superieur a 750 mil':
            weights['>750 mil'] = weight
        elif category == '750 mil':
            weights['750 mil'] = weight
        elif category == '585 mil':
            weights['585 mil'] = weight
        elif category == '375 mil':
            weights['375 mil'] = weight

    return weights


def extract_weights(text):
    # Find all occurrences of patterns like "375 mil = X g"
    mil_weight_matches = re.findall(r'(\d+)\s*mil\s*=\s*(\d+\.?\d*)\s*g', text)

    processed_matches = {f'{mil} mil': float(weight.replace(',', '.')) for mil, weight in mil_weight_matches}

    # Check if there are no specific weight matches
    if not processed_matches:
        # Find the overall weight and assume it corresponds to the single mentioned titrage
        overall_weight_match = re.search(r'(\d+\.?\d*)\s*g', text)
        if overall_weight_match:
            weight = overall_weight_match.group(1)
            # Find the titrage
            mil_match = re.search(r'(\d+)\s*mil', text)
            if mil_match:
                mil = mil_match.group(1)
                return {f'{mil} mil': float(weight)}

    # Convert matches to a dictionary with titrage as keys and weights as values
    return {f'{mil} mil': float(weight) for mil, weight in mil_weight_matches}

def clean_text(text):
    """ Transliterate non-UTF-8 characters to their closest UTF-8 equivalents """
    return unidecode(text)

def docx_table_to_df(doc_path, table_index=0):
    # Load the document
    doc = Document(doc_path)

    # Access the specific table
    table = doc.tables[table_index]

    # Extract and clean data from the table
    data = [[clean_text(cell.text) for cell in row.cells] for row in table.rows]

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Optionally, set the first row as the header
    df.columns = df.iloc[0]
    df = df.drop(0)

    return df

price_per_kg = 59597.52
price_per_g = price_per_kg/1000

# Path to your document
doc_path = '/home/robsonwaves/Documents/dump/CAT_EXPO_181220230.docx'

# Extract the table
df = docx_table_to_df(doc_path)

df['Designation'] = df['Designation'].str.replace(',', '.')
# Assuming 'df' is your DataFrame
# # Apply the extraction function to each row in the "Désignation" column
# weights_data = df['Designation'].apply(extract_weights)
#
# # Create new columns for each titrage and fill with weights
# for titrage in set().union(*weights_data):
#     df[titrage] = weights_data.apply(lambda x: x.get(titrage))

# Créer des colonnes pour chaque titrage dans le DataFrame
for mil in ['>750 mil', '750 mil', '585 mil', '375 mil']:
    df[mil] = None


# Appliquer la fonction d'extraction à chaque ligne
for index, row in df.iterrows():
    weight_info = extract_weights2(row['Designation'])
    for key in weight_info:
        df.at[index, key] = weight_info[key]



def extract_weight_and_separate_by_fineness(row):
    # Initial setup for different fineness categories
    weights = {'>750 mil': None, '750 mil': None, '585 mil': None, '375 mil': None}

    # Regular expressions for finding weight and fineness
    weight_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*g')
    fineness_pattern = re.compile(r'(\d{3,4})\s*mil', re.IGNORECASE)
    superior_pattern = re.compile(r'superieur a\s*(\d+)\s*mil', re.IGNORECASE)

    # Extracting weight
    weight_match = weight_pattern.search(row['Designation'])
    if weight_match:
        weight = float(weight_match.group(1))

        # Determining fineness category and assigning weight
        fineness_match = fineness_pattern.search(row['Designation'])
        superior_match = superior_pattern.search(row['Designation'])
        if fineness_match and not superior_match:
            fineness = fineness_match.group(1) + ' mil'
            weights[fineness] = weight
        elif superior_match:
            fineness = ">" + superior_match.group(1) + ' mil'
            weights[fineness] = weight

    return pd.Series(weights)


mask = df[['>750 mil', '750 mil', '585 mil', '375 mil']].isna() | (df[['>750 mil', '750 mil', '585 mil', '375 mil']] == '')
# Example of usage
# Assuming 'data' is your DataFrame loaded from the Excel file

mask = mask.all(axis=1)

new_columns = df[mask].apply(extract_weight_and_separate_by_fineness, axis=1)
df.update(new_columns)

df.fillna(0, inplace=True)

#df['prix (€)'] = ((df['585 mil'] * 585/1000 + df['375 mil'] * 375/1000 + df['750 mil'] * 750/1000) * price_per_g).round(0)


output_file = '/home/robsonwaves/Documents/dump/' + str(datetime.datetime.now()) + 'path_to_output_file.xlsx'
df.to_excel(output_file, index=False)

# Display the first few rows of the DataFrame
print(df.head())
