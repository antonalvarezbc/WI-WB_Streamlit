import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Diccionario de traducciones
translations = {
    "es": {
        "select_initial_excel": "Selecciona el archivo Excel inicial",
        "browse_excel": "Buscar Excel",
        "no_excel_selected": "No se ha seleccionado ningún archivo Excel",
        "select_images_csv": "Selecciona el archivo CSV de imágenes",
        "browse_csv": "Buscar CSV",
        "no_csv_selected": "No se ha seleccionado ningún archivo CSV",
        "select_deployments_csv": "Selecciona el archivo CSV de deployments",
        "process_multiple_images": "Procesar múltiples imágenes",
        "time_threshold": "Umbral de tiempo (segundos):",
        "process_files": "Procesar Archivos",
        "download_excel": "Descargar Excel Actualizado",
        "process_completed": "Archivos procesados con éxito",
        "error_message": "Se produjo un error: "
    },
    "pt": {
        "select_initial_excel": "Selecione o arquivo Excel inicial",
        "browse_excel": "Procurar Excel",
        "no_excel_selected": "Nenhum arquivo Excel selecionado",
        "select_images_csv": "Selecione o arquivo CSV de imagens",
        "browse_csv": "Procurar CSV",
        "no_csv_selected": "Nenhum arquivo CSV selecionado",
        "select_deployments_csv": "Selecione o arquivo CSV de deployments",
        "process_multiple_images": "Processar múltiplas imagens",
        "time_threshold": "Limite de tempo (segundos):",
        "process_files": "Processar Arquivos",
        "download_excel": "Baixar Excel Atualizado",
        "process_completed": "Arquivos processados com sucesso",
        "error_message": "Ocorreu um erro: "
    },
    "en": {
        "select_initial_excel": "Select the Initial Excel file",
        "browse_excel": "Browse Excel",
        "no_excel_selected": "No Excel file selected",
        "select_images_csv": "Select the Images CSV file",
        "browse_csv": "Browse CSV",
        "no_csv_selected": "No CSV file selected",
        "select_deployments_csv": "Select the Deployments CSV file",
        "process_multiple_images": "Process multiple images",
        "time_threshold": "Time threshold (seconds):",
        "process_files": "Process Files",
        "download_excel": "Download Updated Excel",
        "process_completed": "Files processed successfully",
        "error_message": "An error occurred: "
    }
}

# Función para generar occurrenceID
def generate_occurrence_id(row):
    sanitized_project_id = re.sub(r'[^a-zA-Z0-9-_]', '_', str(row['project_id']) if pd.notna(row['project_id']) else '')
    sanitized_subproject_name = re.sub(r'[^a-zA-Z0-9-_]', '_', str(row['subproject_name']) if pd.notna(row['subproject_name']) else '')
    sanitized_deployment_id = re.sub(r'[^a-zA-Z0-9-_]', '_', str(row['deployment_id']) if pd.notna(row['deployment_id']) else '')
    return f"{sanitized_project_id}-{sanitized_subproject_name}-{sanitized_deployment_id}"

# Asegurar que la extensión del archivo es .JPG
def ensure_jpg_extension(location):
    if pd.isna(location):
        return location
    parts = location.split('.')
    if len(parts) > 1 and parts[-1].lower() != 'jpg':
        return '.'.join(parts[:-1]) + '.JPG'
    return location

# Función para procesar archivos
def process_files(initial_df, images_df, deployments_df, process_multiple_images, time_threshold):
    merged_df = images_df.merge(deployments_df, on=['project_id', 'deployment_id'], suffixes=('_image', '_deployment'))
    result_df = merged_df[['latitude', 'longitude', 'placename', 'location', 'timestamp', 'project_id', 'deployment_id', 'subproject_name']]
    result_df['timestamp'] = pd.to_datetime(result_df['timestamp'], format='%Y-%m-%d %H:%M:%S')

    if process_multiple_images:
        return process_multiple_images_func(result_df, initial_df, time_threshold)
    else:
        combined_df = pd.DataFrame()
        combined_df['Encounter.decimalLatitude'] = result_df['latitude']
        combined_df['Encounter.decimalLongitude'] = result_df['longitude']
        combined_df['Encounter.verbatimLocality'] = result_df['placename']
        combined_df['Encounter.mediaAsset0'] = result_df['location'].apply(lambda x: x.split('/')[-1] if pd.notna(x) else x)
        combined_df['Occurrence.occurrenceID'] = result_df.apply(generate_occurrence_id, axis=1)
        combined_df['Encounter.mediaAsset0'] = combined_df['Encounter.mediaAsset0'].apply(ensure_jpg_extension)
        combined_df['Encounter.year'] = result_df['timestamp'].dt.year
        combined_df['Encounter.month'] = result_df['timestamp'].dt.month
        combined_df['Encounter.day'] = result_df['timestamp'].dt.day
        combined_df['Encounter.hour'] = result_df['timestamp'].dt.hour
        combined_df['Encounter.minutes'] = result_df['timestamp'].dt.minute

        for column in initial_df.columns:
            if column not in combined_df.columns:
                combined_df[column] = initial_df[column].iloc[0]

        final_columns = ['Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude',
                         'Encounter.verbatimLocality', 'Encounter.mediaAsset0', 'Encounter.year', 'Encounter.month',
                         'Encounter.day', 'Encounter.hour', 'Encounter.minutes'] + \
                        [col for col in initial_df.columns if col not in combined_df.columns]

        combined_df = combined_df[final_columns]
        return combined_df

# Función para procesar múltiples imágenes
def process_multiple_images_func(result_df, initial_df, time_threshold):
    result_df = result_df.sort_values(by=['deployment_id', 'timestamp'])
    combined_images = []
    for deployment_id, group in result_df.groupby('deployment_id'):
        group['time_diff'] = group['timestamp'].diff().dt.total_seconds().fillna(time_threshold + 1)
        group_images = []
        for _, row in group.iterrows():
            if group_images and row['time_diff'] > time_threshold:
                combined_images.append(group_images)
                group_images = []
            group_images.append(row)
        if group_images:
            combined_images.append(group_images)

    rows_list = []
    max_assets = 0
    for images_group in combined_images:
        base_row = images_group[0]
        new_row = {
            'Encounter.decimalLatitude': base_row['latitude'],
            'Encounter.decimalLongitude': base_row['longitude'],
            'Encounter.verbatimLocality': base_row['placename'],
            'Occurrence.occurrenceID': generate_occurrence_id(base_row),
            'Encounter.year': base_row['timestamp'].year,
            'Encounter.month': base_row['timestamp'].month,
            'Encounter.day': base_row['timestamp'].day,
            'Encounter.hour': base_row['timestamp'].hour,
            'Encounter.minutes': base_row['timestamp'].minute
        }
        for i, image in enumerate(images_group):
            image_location = image['location'].split('/')[-1]
            new_row[f'Encounter.mediaAsset{i}'] = ensure_jpg_extension(image_location)
        rows_list.append(new_row)
        max_assets = max(max_assets, len(images_group))

    combined_df = pd.DataFrame(rows_list)
    for i in range(max_assets):
        if f'Encounter.mediaAsset{i}' not in combined_df.columns:
            combined_df[f'Encounter.mediaAsset{i}'] = None

    for column in initial_df.columns:
        if column not in combined_df.columns:
            combined_df[column] = initial_df[column].iloc[0]

    return combined_df

# Interfaz de usuario en Streamlit
st.title("LynxAutomator")

# Selector de idioma
lang = st.selectbox("Seleccione el idioma / Select the language", ["es", "en", "pt"])
tr = translations[lang]

# Cargar archivo Excel inicial
initial_excel_file = st.file_uploader(tr["select_initial_excel"], type=['xlsx'])

# Cargar archivo CSV de imágenes
images_csv_file = st.file_uploader(tr["select_images_csv"], type=['csv'])

# Cargar archivo CSV de despliegues
deployments_csv_file = st.file_uploader(tr["select_deployments_csv"], type=['csv'])

# Opciones de procesamiento
process_multiple_images = st.checkbox(tr["process_multiple_images"])
time_threshold = st.number_input(tr["time_threshold"], min_value=1, value=30)

# Botón para procesar archivos
if st.button(tr["process_files"]):
    if initial_excel_file and images_csv_file and deployments_csv_file:
        try:
            # Cargar los archivos
            initial_df = pd.read_excel(initial_excel_file)
            images_df = pd.read_csv(images_csv_file, dtype=str)
            deployments_df = pd.read_csv(deployments_csv_file, dtype=str)

            # Procesar los archivos
            final_df = process_files(initial_df, images_df, deployments_df, process_multiple_images, time_threshold)

            # Mostrar una tabla con los resultados procesados
            st.success(tr["process_completed"])
            st.dataframe(final_df)

            # Botón para descargar el archivo Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False)
            st.download_button(label=tr["download_excel"], data=buffer, file_name="resultados.xlsx", mime="application/vnd.ms-excel")

        except Exception as e:
            st.error(f"{tr['error_message']}{e}")
    else:
        st.error(tr["no_excel_selected"] if not initial_excel_file else tr["no_csv_selected"])
