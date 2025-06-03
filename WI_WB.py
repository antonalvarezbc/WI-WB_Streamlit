import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os # Added for potential future use, though not strictly necessary for current ExcelCombinerApp port

# Diccionario de traducciones (updated)
translations = {
    "es": {
        "select_initial_excel": "Selecciona el archivo Excel inicial",
        "browse_excel": "Buscar Excel",
        "no_excel_selected": "No se ha seleccionado ningún archivo Excel",
        "select_images_csv": "Selecciona el archivo CSV de imágenes",
        "browse_csv": "Buscar CSV",
        "no_csv_selected": "No se ha seleccionado ningún archivo CSV",
        "select_deployments_csv": "Selecciona el archivo CSV de deployments",
        "process_multiple_images": "Procesar múltiples imágenes (agrupar por tiempo)",
        "time_threshold": "Umbral de tiempo (segundos):",
        "process_files": "Procesar Archivos",
        "download_excel": "Descargar Excel Actualizado",
        "process_completed": "Archivos procesados con éxito.",
        "error_message": "Se produjo un error: ",
        "separate_objects_gt_1": "Procesar imágenes con >1 objeto individualmente",
        "missing_columns_error": "Columnas 'project_id' o 'deployment_id' faltan en los archivos CSV de imágenes o despliegues. Asegúrate de que ambos archivos contengan estas columnas.",
        "error_column_missing_in_images_csv": "La columna '{col}' falta en el archivo CSV de imágenes.",
        "error_column_missing_in_deployments_csv": "La columna '{col}' falta en el archivo CSV de deployments.",
        "error_required_column_missing_in_merged_csv": "La columna requerida '{col}' falta en los datos combinados de imágenes/despliegues.",
        "error_no_initial_excel_selected": "No se ha seleccionado un archivo de Excel inicial.",
        "file_saved_successfully": "Archivo guardado con éxito en {path}", # Primarily for Tkinter, but good to have
        "error_threshold_value": "El umbral de tiempo debe ser un número entero positivo.",
        "warning_empty_final_df": "El DataFrame final está vacío, pero había datos para procesar. Verifique los filtros y umbrales.",
        "info_no_valid_data": "No había datos válidos para procesar después de la carga inicial y combinación.",
        "error_saving_file": "No se pudo guardar el archivo: ", # Primarily for Tkinter
        "warning_download_empty": "No hay datos procesados para descargar. El Excel resultante estaría vacío.",
        "error_download_not_available": "Los archivos aún no se han procesado o el procesamiento no generó datos.",
        "error_initial_excel_empty": "El archivo Excel inicial está vacío o no se pudo leer.",
        "error_timestamp_conversion": "Error al convertir 'timestamp'. Asegúrese de que el formato sea correcto (YYYY-MM-DD HH:MM:SS). Filas con timestamps inválidos serán omitidas."
    },
    "pt": {
        "select_initial_excel": "Selecione o arquivo Excel inicial",
        "browse_excel": "Procurar Excel",
        "no_excel_selected": "Nenhum arquivo Excel selecionado",
        "select_images_csv": "Selecione o arquivo CSV de imagens",
        "browse_csv": "Procurar CSV",
        "no_csv_selected": "Nenhum arquivo CSV selecionado",
        "select_deployments_csv": "Selecione o arquivo CSV de deployments",
        "process_multiple_images": "Processar múltiplas imagens (agrupar por tempo)",
        "time_threshold": "Limite de tempo (segundos):",
        "process_files": "Processar Arquivos",
        "download_excel": "Baixar Excel Atualizado",
        "process_completed": "Arquivos processados com sucesso.",
        "error_message": "Ocorreu um erro: ",
        "separate_objects_gt_1": "Processar imagens com >1 objeto individualmente",
        "missing_columns_error": "Colunas 'project_id' ou 'deployment_id' estão faltando nos arquivos CSV de imagens ou implantações. Certifique-se de que ambos os arquivos contenham essas colunas.",
        "error_column_missing_in_images_csv": "A coluna '{col}' está faltando no arquivo CSV de imagens.",
        "error_column_missing_in_deployments_csv": "A coluna '{col}' está faltando no arquivo CSV de implantações.",
        "error_required_column_missing_in_merged_csv": "A coluna necessária '{col}' falta nos dados combinados de imagens/implantações.",
        "error_no_initial_excel_selected": "Nenhum arquivo Excel inicial foi selecionado.",
        "file_saved_successfully": "Arquivo salvo com sucesso em {path}",
        "error_threshold_value": "O limite de tempo deve ser um número inteiro positivo.",
        "warning_empty_final_df": "O DataFrame final está vazio, mas havia dados para processar. Verifique os filtros e limites.",
        "info_no_valid_data": "Não havia dados válidos para processar após o carregamento inicial e a combinação.",
        "error_saving_file": "Não foi possível salvar o arquivo: ",
        "warning_download_empty": "Não há dados processados para download. O Excel resultante estaria vazio.",
        "error_download_not_available": "Os arquivos ainda não foram processados ou o processamento não gerou dados.",
        "error_initial_excel_empty": "O arquivo Excel inicial está vazio ou não pôde ser lido.",
        "error_timestamp_conversion": "Erro ao converter 'timestamp'. Certifique-se de que o formato esteja correto (AAAA-MM-DD HH:MM:SS). Linhas com timestamps inválidos serão omitidas."
    },
    "en": {
        "select_initial_excel": "Select the Initial Excel file",
        "browse_excel": "Browse Excel",
        "no_excel_selected": "No Excel file selected",
        "select_images_csv": "Select the Images CSV file",
        "browse_csv": "Browse CSV",
        "no_csv_selected": "No CSV file selected",
        "select_deployments_csv": "Select the Deployments CSV file",
        "process_multiple_images": "Process multiple images (group by time)",
        "time_threshold": "Time threshold (seconds):",
        "process_files": "Process Files",
        "download_excel": "Download Updated Excel",
        "process_completed": "Files processed successfully.",
        "error_message": "An error occurred: ",
        "separate_objects_gt_1": "Process images with >1 object individually",
        "missing_columns_error": "Columns 'project_id' or 'deployment_id' are missing in the images or deployments CSV files. Ensure both files contain these columns.",
        "error_column_missing_in_images_csv": "Column '{col}' is missing in the images CSV file.",
        "error_column_missing_in_deployments_csv": "Column '{col}' is missing in the deployments CSV file.",
        "error_required_column_missing_in_merged_csv": "Required column '{col}' is missing in the merged images/deployments data.",
        "error_no_initial_excel_selected": "No initial Excel file has been selected.",
        "file_saved_successfully": "File saved successfully to {path}",
        "error_threshold_value": "Time threshold must be a positive integer.",
        "warning_empty_final_df": "The final DataFrame is empty, but there was data to process. Check filters and thresholds.",
        "info_no_valid_data": "No valid data was found to process after initial load and merge.",
        "error_saving_file": "Could not save file: ",
        "warning_download_empty": "No processed data available for download. The resulting Excel would be empty.",
        "error_download_not_available": "Files have not been processed yet or processing resulted in no data.",
        "error_initial_excel_empty": "The initial Excel file is empty or could not be read.",
        "error_timestamp_conversion": "Error converting 'timestamp'. Ensure format is YYYY-MM-DD HH:MM:SS. Rows with invalid timestamps will be omitted."
    }
}

# Función para generar occurrenceID (adapted from ExcelCombinerApp)
def generate_occurrence_id(row):
    # Sanitized project_id and deployment_id as per ExcelCombinerApp's simple string conversion.
    # WI_WB.py's original re.sub was more robust for characters, but ExcelCombinerApp uses simple string.
    # To match ExcelCombinerApp, subproject_name is NOT included here.
    sanitized_project_id = str(row['project_id']) if pd.notna(row['project_id']) else ''
    sanitized_deployment_id = str(row['deployment_id']) if pd.notna(row['deployment_id']) else ''
    return f"{sanitized_project_id}-{sanitized_deployment_id}"

# Asegurar que la extensión del archivo es .JPG (adapted from ExcelCombinerApp)
def ensure_jpg_extension(location):
    if pd.isna(location):
        return pd.NA # Use pd.NA for consistency
    location_str = str(location)
    parts = location_str.split('.')
    if len(parts) > 1: # If has an extension
        base_name = '.'.join(parts[:-1])
        return base_name + '.JPG' # Standardizes to .JPG
    return location_str + '.JPG' # If no extension, adds .JPG

# Función para procesar una sola imagen por fila (New, adapted from ExcelCombinerApp)
def process_single_image_per_row(result_df_input, initial_df_template):
    result_df = result_df_input.copy().reset_index(drop=True)
    initial_df = initial_df_template.copy()

    combined_rows = []

    for _, row in result_df.iterrows():
        new_row_dict = {}
        new_row_dict['Encounter.decimalLatitude'] = row['latitude']
        new_row_dict['Encounter.decimalLongitude'] = row['longitude']
        new_row_dict['Encounter.verbatimLocality'] = row['placename']
        
        media_asset = row['location']
        if pd.notna(media_asset):
            new_row_dict['Encounter.mediaAsset0'] = ensure_jpg_extension(media_asset.split('/')[-1])
        else:
            new_row_dict['Encounter.mediaAsset0'] = pd.NA

        new_row_dict['Occurrence.occurrenceID'] = generate_occurrence_id(row)
        
        ts = row['timestamp'] # Assumed to be datetime object already
        new_row_dict['Encounter.year'] = ts.year
        new_row_dict['Encounter.month'] = ts.month
        new_row_dict['Encounter.day'] = ts.day
        new_row_dict['Encounter.hour'] = ts.hour
        new_row_dict['Encounter.minutes'] = ts.minute

        for col_template in initial_df.columns:
            if col_template not in new_row_dict:
                new_row_dict[col_template] = initial_df[col_template].iloc[0] if not initial_df.empty and col_template in initial_df and not initial_df[col_template].empty else pd.NA
        
        combined_rows.append(new_row_dict)

    if not combined_rows:
        temp_final_cols = list(initial_df.columns)
        default_cols_to_ensure = ['Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude', 
                                  'Encounter.verbatimLocality', 'Encounter.mediaAsset0', 'Encounter.year', 
                                  'Encounter.month', 'Encounter.day', 'Encounter.hour', 'Encounter.minutes']
        for c in default_cols_to_ensure:
            if c not in temp_final_cols:
                temp_final_cols.insert(0, c)
        return pd.DataFrame(columns=list(dict.fromkeys(temp_final_cols)))

    combined_df = pd.DataFrame(combined_rows)
    
    final_ordered_columns = [
        'Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude',
        'Encounter.verbatimLocality', 'Encounter.mediaAsset0', 
        'Encounter.year', 'Encounter.month', 'Encounter.day', 
        'Encounter.hour', 'Encounter.minutes'
    ]
    
    for col in initial_df.columns:
        if col not in final_ordered_columns and col in combined_df.columns:
            final_ordered_columns.append(col)
    
    for col in combined_df.columns: # Add any other generated columns not in initial_df or the main list
        if col not in final_ordered_columns:
            final_ordered_columns.append(col)
            
    combined_df = combined_df.reindex(columns=final_ordered_columns, fill_value=pd.NA)
    return combined_df

# Función para procesar múltiples imágenes (Updated, adapted from ExcelCombinerApp)
def process_multiple_images_func(result_df_input, initial_df_template, time_threshold, current_lang_tr):
    result_df = result_df_input.copy().reset_index(drop=True)
    initial_df = initial_df_template.copy()

    if not isinstance(time_threshold, int) or time_threshold <= 0:
        st.error(current_lang_tr["error_threshold_value"])
        # Return empty DataFrame with initial_df schema if threshold is invalid
        # This part is tricky as we need a schema that includes potential mediaAssets
        # For simplicity, return an empty DataFrame or one based on initial_df
        return pd.DataFrame(columns=initial_df.columns)


    # Ensure 'timestamp' is datetime
    if not pd.api.types.is_datetime64_any_dtype(result_df['timestamp']):
        result_df['timestamp'] = pd.to_datetime(result_df['timestamp'], errors='coerce')
        result_df = result_df.dropna(subset=['timestamp'])

    if result_df.empty:
        # Construct empty DataFrame with expected schema
        temp_final_cols = list(initial_df.columns)
        default_cols_to_ensure = ['Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude', 
                                  'Encounter.verbatimLocality', 'Encounter.year', 
                                  'Encounter.month', 'Encounter.day', 'Encounter.hour', 'Encounter.minutes']
        # Ensure at least 'Encounter.mediaAsset0' for schema if empty
        default_cols_to_ensure.append('Encounter.mediaAsset0')
        for c in default_cols_to_ensure:
            if c not in temp_final_cols:
                temp_final_cols.insert(0, c)
        return pd.DataFrame(columns=list(dict.fromkeys(temp_final_cols)))

    result_df = result_df.sort_values(by=['deployment_id', 'timestamp'])
    
    all_processed_rows = []
    max_assets_in_any_group = 0

    for _, group_df in result_df.groupby('deployment_id'):
        current_group_processed = group_df.copy().reset_index(drop=True)
        current_group_processed['time_diff'] = current_group_processed['timestamp'].diff().dt.total_seconds().fillna(time_threshold + 1)
        
        image_event_accumulator = []
        
        for _, image_row in current_group_processed.iterrows():
            if image_event_accumulator and image_row['time_diff'] > time_threshold:
                if image_event_accumulator:
                    base_event_row_data = image_event_accumulator[0]
                    new_combined_row = {
                        'Encounter.decimalLatitude': base_event_row_data['latitude'],
                        'Encounter.decimalLongitude': base_event_row_data['longitude'],
                        'Encounter.verbatimLocality': base_event_row_data['placename'],
                        'Occurrence.occurrenceID': generate_occurrence_id(base_event_row_data),
                        'Encounter.year': base_event_row_data['timestamp'].year,
                        'Encounter.month': base_event_row_data['timestamp'].month,
                        'Encounter.day': base_event_row_data['timestamp'].day,
                        'Encounter.hour': base_event_row_data['timestamp'].hour,
                        'Encounter.minutes': base_event_row_data['timestamp'].minute
                    }
                    for i, asset_data_row in enumerate(image_event_accumulator):
                        asset_location = asset_data_row['location']
                        new_combined_row[f'Encounter.mediaAsset{i}'] = ensure_jpg_extension(asset_location.split('/')[-1]) if pd.notna(asset_location) else pd.NA
                    
                    all_processed_rows.append(new_combined_row)
                    max_assets_in_any_group = max(max_assets_in_any_group, len(image_event_accumulator))
                    image_event_accumulator = []
            
            image_event_accumulator.append(image_row)
        
        if image_event_accumulator: # Process remaining images in accumulator
            base_event_row_data = image_event_accumulator[0]
            new_combined_row = {
                'Encounter.decimalLatitude': base_event_row_data['latitude'],
                'Encounter.decimalLongitude': base_event_row_data['longitude'],
                'Encounter.verbatimLocality': base_event_row_data['placename'],
                'Occurrence.occurrenceID': generate_occurrence_id(base_event_row_data),
                'Encounter.year': base_event_row_data['timestamp'].year,
                'Encounter.month': base_event_row_data['timestamp'].month,
                'Encounter.day': base_event_row_data['timestamp'].day,
                'Encounter.hour': base_event_row_data['timestamp'].hour,
                'Encounter.minutes': base_event_row_data['timestamp'].minute
            }
            for i, asset_data_row in enumerate(image_event_accumulator):
                asset_location = asset_data_row['location']
                new_combined_row[f'Encounter.mediaAsset{i}'] = ensure_jpg_extension(asset_location.split('/')[-1]) if pd.notna(asset_location) else pd.NA

            all_processed_rows.append(new_combined_row)
            max_assets_in_any_group = max(max_assets_in_any_group, len(image_event_accumulator))

    if not all_processed_rows:
        temp_final_cols = list(initial_df.columns)
        default_cols_to_ensure = ['Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude', 
                                  'Encounter.verbatimLocality', 'Encounter.year', 
                                  'Encounter.month', 'Encounter.day', 'Encounter.hour', 'Encounter.minutes']
        for i in range(max_assets_in_any_group if max_assets_in_any_group > 0 else 1): # Ensure at least mediaAsset0
            default_cols_to_ensure.append(f'Encounter.mediaAsset{i}')
        for c in default_cols_to_ensure:
            if c not in temp_final_cols:
                temp_final_cols.insert(0, c)
        return pd.DataFrame(columns=list(dict.fromkeys(temp_final_cols)))

    final_combined_df = pd.DataFrame(all_processed_rows)

    for i in range(max_assets_in_any_group):
        col_name = f'Encounter.mediaAsset{i}'
        if col_name not in final_combined_df.columns:
            final_combined_df[col_name] = pd.NA

    for col_template in initial_df.columns:
        if col_template not in final_combined_df.columns:
            final_combined_df[col_template] = initial_df[col_template].iloc[0] if not initial_df.empty and col_template in initial_df and not initial_df[col_template].empty else pd.NA
    
    ordered_cols = [
        'Occurrence.occurrenceID', 'Encounter.decimalLatitude', 'Encounter.decimalLongitude',
        'Encounter.verbatimLocality', 'Encounter.year', 'Encounter.month', 'Encounter.day',
        'Encounter.hour', 'Encounter.minutes'
    ]
    media_asset_cols_sorted = sorted(
        [col for col in final_combined_df.columns if col.startswith('Encounter.mediaAsset')],
        key=lambda x: int(x.replace('Encounter.mediaAsset', ''))
    )
    ordered_cols.extend(media_asset_cols_sorted)

    for col in initial_df.columns:
        if col not in ordered_cols and col in final_combined_df.columns:
            ordered_cols.append(col)
            
    for col in final_combined_df.columns: # Add any other generated columns
        if col not in ordered_cols:
            ordered_cols.append(col)
            
    final_combined_df = final_combined_df.reindex(columns=ordered_cols, fill_value=pd.NA)
    return final_combined_df


# Función para procesar archivos (Main logic, significantly updated from ExcelCombinerApp)
def process_files_main(initial_excel_path, images_csv_path, deployments_csv_path, 
                       process_multiple_images_opt, time_threshold_opt, separate_large_groups_opt, current_lang_tr):
    try:
        # Load initial Excel
        if not initial_excel_path:
            st.error(current_lang_tr["error_no_initial_excel_selected"])
            return None
        
        # Use BytesIO as Streamlit file uploader gives file-like objects
        initial_df_dict = pd.read_excel(initial_excel_path, sheet_name=None)
        if not initial_df_dict:
            st.error(current_lang_tr["error_initial_excel_empty"])
            return None
        first_sheet_name = list(initial_df_dict.keys())[0]
        initial_df = initial_df_dict[first_sheet_name].reset_index(drop=True)

        # Load CSVs
        images_df = pd.read_csv(images_csv_path, dtype=str, low_memory=False)
        deployments_df = pd.read_csv(deployments_csv_path, dtype=str, low_memory=False)

        # --- START: Verificaciones de columnas esenciales para la fusión ---
        required_merge_cols = ['project_id', 'deployment_id']
        for col in required_merge_cols:
            if col not in images_df.columns:
                st.error(current_lang_tr["error_column_missing_in_images_csv"].format(col=col))
                return None
            if col not in deployments_df.columns:
                st.error(current_lang_tr["error_column_missing_in_deployments_csv"].format(col=col))
                return None
        
        merged_df = images_df.merge(deployments_df, on=['project_id', 'deployment_id'], suffixes=('_image', '_deployment'))
        merged_df = merged_df.reset_index(drop=True)

        required_cols_for_result_df = ['latitude', 'longitude', 'placename', 'location', 'timestamp', 'project_id', 'deployment_id', 'subproject_name'] # subproject_name is in ExcelCombinerApp's list
        
        # Add 'number_of_objects' if not present, default to '1'
        if 'number_of_objects' not in merged_df.columns:
            merged_df['number_of_objects'] = '1' 
        
        # Ensure all required columns exist in merged_df
        for col in required_cols_for_result_df:
            if col not in merged_df.columns:
                st.error(current_lang_tr["error_required_column_missing_in_merged_csv"].format(col=col))
                return None
        
        # Always include 'number_of_objects' in the selection if it wasn't already in required_cols_for_result_df (it wasn't)
        cols_to_select_for_result = required_cols_for_result_df + ['number_of_objects']
        result_df = merged_df[list(dict.fromkeys(cols_to_select_for_result))].copy() # list(dict.fromkeys()) to ensure unique cols
            
        # Convert timestamp
        original_row_count = len(result_df)
        result_df['timestamp'] = pd.to_datetime(result_df['timestamp'], errors='coerce')
        result_df = result_df.dropna(subset=['timestamp'])
        if len(result_df) < original_row_count:
            st.warning(current_lang_tr["error_timestamp_conversion"])


        if result_df.empty:
            st.info(current_lang_tr["info_no_valid_data"])
            return pd.DataFrame() # Return empty DataFrame

        final_df = pd.DataFrame()

        if separate_large_groups_opt:
            if 'number_of_objects' not in result_df.columns: # Should be there by now
                 result_df['number_of_objects'] = '1' 
            
            result_df['number_of_objects'] = pd.to_numeric(result_df['number_of_objects'], errors='coerce').fillna(0)
            
            large_objects_df = result_df[result_df['number_of_objects'] > 1].copy().reset_index(drop=True)
            other_objects_df = result_df[result_df['number_of_objects'] <= 1].copy().reset_index(drop=True)

            processed_dfs = []

            if not large_objects_df.empty:
                # Images with >1 object are always processed one image per row
                processed_large_df = process_single_image_per_row(large_objects_df, initial_df)
                processed_dfs.append(processed_large_df)

            if not other_objects_df.empty:
                if process_multiple_images_opt:
                    processed_other_df = process_multiple_images_func(other_objects_df, initial_df, time_threshold_opt, current_lang_tr)
                else:
                    processed_other_df = process_single_image_per_row(other_objects_df, initial_df)
                processed_dfs.append(processed_other_df)
            
            if processed_dfs:
                final_df = pd.concat(processed_dfs, ignore_index=True)
            else: # If both large_objects_df and other_objects_df were empty or resulted in empty processed DFs
                final_df = pd.DataFrame()


        else: # Not separating by 'number_of_objects'
            if process_multiple_images_opt:
                final_df = process_multiple_images_func(result_df.copy(), initial_df, time_threshold_opt, current_lang_tr)
            else:
                final_df = process_single_image_per_row(result_df.copy(), initial_df)
        
        # Final messages
        if final_df is None: # Should not happen if functions return empty DFs instead of None
            st.error(current_lang_tr["error_message"] + "Processing returned None.")
            return pd.DataFrame()
            
        if final_df.empty and not result_df.empty : # result_df had data, but final_df is empty
            st.warning(current_lang_tr["warning_empty_final_df"])
        elif final_df.empty and result_df.empty: # result_df was empty initially
            st.info(current_lang_tr["info_no_valid_data"]) # Already shown above, but good fallback
        elif not final_df.empty:
            st.success(current_lang_tr["process_completed"])
        
        return final_df

    except ValueError as ve:
        st.error(f"{current_lang_tr['error_message']}{ve}")
        return None
    except KeyError as ke:
        st.error(f"{current_lang_tr['error_message']}Missing critical column in input files: {ke}. Please check file contents and structure.")
        return None
    except Exception as e:
        st.error(f"{current_lang_tr['error_message']}{e}")
        # import traceback # For more detailed debugging if needed
        # st.error(traceback.format_exc())
        return None


# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("LynxAutomator WI Wb")

# Language selector
lang_options = list(translations.keys())
lang_selected_label = "Seleccione el idioma / Select the language / Selecione o idioma"
# Use a consistent key for the language selector itself, or show all options
lang = st.sidebar.selectbox(lang_selected_label, lang_options, format_func=lambda x: {"es": "Español", "en": "English", "pt": "Português"}[x])
tr = translations[lang]

st.sidebar.header(tr["select_initial_excel"])
initial_excel_file = st.sidebar.file_uploader(tr["browse_excel"], type=['xlsx', 'xls'], label_visibility="collapsed")

st.sidebar.header(tr["select_images_csv"])
images_csv_file = st.sidebar.file_uploader(tr["browse_csv"] + " (Images)", type=['csv'], label_visibility="collapsed")

st.sidebar.header(tr["select_deployments_csv"])
deployments_csv_file = st.sidebar.file_uploader(tr["browse_csv"] + " (Deployments)", type=['csv'], label_visibility="collapsed")

st.sidebar.header("Opciones de Procesamiento")
# Checkbox for "Process multiple images (group by time)"
process_multiple_images_st = st.sidebar.checkbox(tr["process_multiple_images"], value=False) # Default to False like ExcelCombinerApp for this particular option when it's one of two main paths.

# Checkbox for "Separate if objects > 1"
separate_large_groups_st = st.sidebar.checkbox(tr["separate_objects_gt_1"], value=False) # Default False

# Time threshold input
time_threshold_st = st.sidebar.number_input(tr["time_threshold"], min_value=1, value=3) # ExcelCombinerApp default is 3


if 'final_df' not in st.session_state:
    st.session_state.final_df = None

# Process button
if st.sidebar.button(tr["process_files"]):
    if initial_excel_file and images_csv_file and deployments_csv_file:
        st.session_state.final_df = process_files_main(
            initial_excel_file, 
            images_csv_file, 
            deployments_csv_file,
            process_multiple_images_st, 
            time_threshold_st,
            separate_large_groups_st,
            tr # Pass current language translations
        )
    else:
        missing_files_msg = ""
        if not initial_excel_file: missing_files_msg += tr["no_excel_selected"] + " "
        if not images_csv_file or not deployments_csv_file: missing_files_msg += tr["no_csv_selected"]
        st.sidebar.error(missing_files_msg.strip())
        st.session_state.final_df = None # Clear previous results if files are missing

# Display results and download button
if st.session_state.final_df is not None:
    if not st.session_state.final_df.empty:
        st.dataframe(st.session_state.final_df)
        
        buffer = BytesIO()
        # Use openpyxl as xlsxwriter might have issues in some restricted Streamlit envs for complex files, though usually fine.
        # ExcelCombinerApp implicitly uses default engine of to_excel which is often openpyxl for .xlsx
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer: # Matched default engine often used
            st.session_state.final_df.to_excel(writer, index=False, sheet_name='Results')
        
        st.download_button(
            label=tr["download_excel"],
            data=buffer,
            file_name="resultados_procesados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # Correct MIME for .xlsx
        )
    else:
        # If final_df is an empty DataFrame, it means processing might have occurred but yielded no results
        # Messages for this are handled within process_files_main now.
        # We can add a specific message here if needed, e.g., "Processing complete, no data to display."
        pass

elif st.session_state.final_df is None and not (initial_excel_file and images_csv_file and deployments_csv_file):
    # This case might be if the button wasn't pressed yet or if files were deselected after an error
    pass
