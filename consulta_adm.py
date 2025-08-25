import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import io
import base64

def mostrar_interfaz(BD_ADM):
    # asegurar que Fecha_Corte sea tipo fecha
    BD_ADM['Fecha_Corte'] = pd.to_datetime(BD_ADM['Fecha_Corte'], errors='coerce')
    filtro_actual = pd.DataFrame()

    # --- Filtro Administrado ---
    adm_input = widgets.Text(
        placeholder='Buscar administrado...',
        description='Buscar Administrado',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '150px'}
    )
    adm_select = widgets.SelectMultiple(
        options=sorted(BD_ADM['NOMB_ADM'].dropna().unique().tolist()),
        description='Administrado:',
        rows=6,
        layout=widgets.Layout(width='600px', height='120px'),
        style={'description_width': '150px'}
    )

    def actualizar_adm(change):
        texto = change['new']
        opciones = sorted(BD_ADM['NOMB_ADM'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [a for a in opciones if texto.lower() in str(a).lower()]
            adm_select.options = filtradas[:100]
        else:
            adm_select.options = opciones[:100]

    adm_input.observe(actualizar_adm, names='value')

    # --- Filtro Unidad Fiscalizable ---
    uf_input = widgets.Text(
        placeholder='Buscar Unidad Fiscalizable',
        description='Buscar Unidad Fiscalizable',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '150px'}
    )
    uf_select = widgets.SelectMultiple(
        options=sorted(BD_ADM['NOMB_UF'].dropna().unique().tolist()),
        description='Unidad Fiscalizable:',
        rows=6,
        layout=widgets.Layout(width='600px', height='120px'),
        style={'description_width': '150px'}
    )

    def actualizar_uf(change):
        texto = change['new']
        opciones = sorted(BD_ADM['NOMB_UF'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [u for u in opciones if texto.lower() in str(u).lower()]
            uf_select.options = filtradas[:100]
        else:
            uf_select.options = opciones[:100]

    uf_input.observe(actualizar_uf, names='value')

    # --- Filtro Departamento ---
    dpto_input = widgets.Text(
        placeholder='Buscar Departamento...',
        description='Buscar Dpto:',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '150px'}
    )
    dpto_select = widgets.SelectMultiple(
        options=sorted(BD_ADM['DPTO'].dropna().unique().tolist()),
        description='Departamento:',
        rows=6,
        layout=widgets.Layout(width='600px', height='120px'),
        style={'description_width': '150px'}
    )

    def actualizar_dpto(change):
        texto = change['new']
        opciones = sorted(BD_ADM['DPTO'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [d for d in opciones if texto.lower() in str(d).lower()]
            dpto_select.options = filtradas[:100]
        else:
            dpto_select.options = opciones[:100]

    dpto_input.observe(actualizar_dpto, names='value')

    # --- Filtro Fecha ---
    fecha_min = BD_ADM['Fecha_Corte'].min().date()
    fecha_max = BD_ADM['Fecha_Corte'].max().date()

    fecha_inicio = widgets.DatePicker(
        description='Desde:',
        value=fecha_min,
        style={'description_width': 'initial'}
    )
    fecha_fin = widgets.DatePicker(
        description='Hasta:',
        value=fecha_max,
        style={'description_width': 'initial'}
    )

    # --- Salida de tabla ---
    output_tabla = widgets.Output()
    output_descarga = widgets.Output()
    boton_descarga = widgets.Button(description="📥 Descargar Excel", button_style='success')

    def update_summary(adm, uf, dpto, fecha_inicio_val, fecha_fin_val):
        nonlocal filtro_actual
        output_tabla.clear_output()

        df = BD_ADM.copy()
        if adm:
            df = df[df['NOMB_ADM'].isin(adm)]
        if uf:
            df = df[df['NOMB_UF'].isin(uf)]
        if dpto:
            df = df[df['DPTO'].isin(dpto)]
        if fecha_inicio_val and fecha_fin_val:
            df = df[
                (df['Fecha_Corte'].dt.date >= fecha_inicio_val) &
                (df['Fecha_Corte'].dt.date <= fecha_fin_val)
            ]

        filtro_actual = df.copy()

        columnas_resumen = [
            'COD_ADM','NUM_DOC','NOMB_ADM','NOMB_UF',
            'COD_UF','SUBSECT','DPTO','Fecha_Corte','Estado'
        ]
        df_resumen = df[columnas_resumen]

        with output_tabla:
            display(HTML('<h3 style="color:#002060;">📋 Resumen de Registros</h3>'))
            if df_resumen.empty:
                display(HTML('<p style="color:red;">⚠️ No se encontraron registros con los filtros seleccionados.</p>'))
            else:
                display(df_resumen)

    # función descarga
    def descargar_excel(b):
        if not filtro_actual.empty:
            buffer = io.BytesIO()
            filtro_actual.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode()
            href = f'<a download="consulta_adm.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded}" target="_blank">📄 Descargar Excel</a>'
            with output_descarga:
                output_descarga.clear_output()
                display(HTML(href))
        else:
            with output_descarga:
                output_descarga.clear_output()
                print("⚠️ No hay datos filtrados para descargar.")

    boton_descarga.on_click(descargar_excel)

    # --- Interfaz completa ---
    filtros = widgets.VBox([
        widgets.HTML('<h2 style="color:#002060;">🔎 Entorno de consulta BD_ADM</h2>'),
        widgets.HBox([adm_input]),
        widgets.HBox([adm_select]),
        widgets.HBox([uf_input]),
        widgets.HBox([uf_select]),
        widgets.HBox([dpto_input]),
        widgets.HBox([dpto_select]),
        widgets.HTML('<h4 style="color:#002060;">Filtrar por Fecha de Corte</h4>'),
        widgets.HBox([fecha_inicio, fecha_fin]),
        boton_descarga,
        output_descarga
    ])

    interactiva = widgets.interactive_output(update_summary, {
        'adm': adm_select,
        'uf': uf_select,
        'dpto': dpto_select,
        'fecha_inicio_val': fecha_inicio,
        'fecha_fin_val': fecha_fin
    })

    display(filtros, interactiva, output_tabla)
