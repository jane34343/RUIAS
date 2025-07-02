# archivo: uf_ruias.py

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import io
import base64

def mostrar_interfaz_uf(BD_RUIAS1):
    BD_RUIAS1['F_RESOL_RD'] = pd.to_datetime(BD_RUIAS1['F_RESOL_RD'], errors='coerce')
    filtro_actual = pd.DataFrame()

    # --- Filtros: RUC ---
    ruc_input = widgets.Text(
        placeholder='Buscar RUC...',
        description='Buscar RUC:',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '250px'}
    )
    ruc_select = widgets.SelectMultiple(
        options=sorted(BD_RUIAS1['NUM_DOC'].dropna().unique().tolist()),
        description='Seleccionar RUC:',
        rows=5,
        layout=widgets.Layout(width='600px', height='110px'),
        style={'description_width': '250px'}
    )

    def actualizar_ruc(change):
        texto = change['new']
        opciones = sorted(BD_RUIAS1['NUM_DOC'].dropna().unique().tolist())
        if len(texto) >= 2:
            ruc_select.options = [r for r in opciones if texto.lower() in str(r).lower()][:100]
        else:
            ruc_select.options = opciones[:100]

    ruc_input.observe(actualizar_ruc, names='value')

    # --- Filtros: UF ---
    uf_input = widgets.Text(
        placeholder='Buscar Unidad Fiscalizable',
        description='Buscar:',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '250px'}
    )
    uf_select = widgets.SelectMultiple(
        options=sorted(BD_RUIAS1['UF'].dropna().unique().tolist()),
        description='Seleccionar Unidad Fiscalizable',
        rows=5,
        layout=widgets.Layout(width='600px', height='110px'),
        style={'description_width': '250px'}
    )

    def actualizar_uf(change):
        texto = change['new']
        opciones = sorted(BD_RUIAS1['UF'].dropna().unique().tolist())
        if len(texto) >= 2:
            uf_select.options = [u for u in opciones if texto.lower() in str(u).lower()][:100]
        else:
            uf_select.options = opciones[:100]

    uf_input.observe(actualizar_uf, names='value')

    # --- Filtros: Departamento ---
    dpto_input = widgets.Text(
        placeholder='Buscar Departamento...', 
        description='Buscar:',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '250px'}
    )
    dpto_select = widgets.SelectMultiple(
        options=sorted(BD_RUIAS1['DPTO'].dropna().unique().tolist()),
        description='Seleccionar Departamento:',
        rows=5,
        layout=widgets.Layout(width='600px', height='110px'),
        style={'description_width': '250px'}
    )

    def actualizar_dpto(change):
        texto = change['new']
        opciones = sorted(BD_RUIAS1['DPTO'].dropna().unique().tolist())
        if len(texto) >= 2:
            dpto_select.options = [d for d in opciones if texto.lower() in str(d).lower()][:100]
        else:
            dpto_select.options = opciones[:100]

    dpto_input.observe(actualizar_dpto, names='value')

    # --- Fechas ---
    fecha_min = BD_RUIAS1['F_RESOL_RD'].min().date()
    fecha_max = BD_RUIAS1['F_RESOL_RD'].max().date()

    fecha_inicio = widgets.DatePicker(
        description='Desde:',
        value=fecha_min,
        disabled=False,
        style={'description_width': 'initial'}
    )

    fecha_fin = widgets.DatePicker(
        description='Hasta:',
        value=fecha_max,
        disabled=False,
        style={'description_width': 'initial'}
    )

    # --- Botón descarga ---
    boton_descarga = widgets.Button(description="📥 Descargar base filtrada", button_style='success')
    output_descarga = widgets.Output()

    def descargar_excel(b):
        if not filtro_actual.empty:
            buffer = io.BytesIO()
            filtro_actual.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode()
            href = f'<a download="base_filtrada.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded}" target="_blank">📄 Descargar Excel</a>'
            with output_descarga:
                output_descarga.clear_output()
                display(HTML(href))
        else:
            with output_descarga:
                output_descarga.clear_output()
                print("⚠️ No hay datos filtrados para descargar.")

    boton_descarga.on_click(descargar_excel)

    # --- Tabla de salida ---
    output_tabla = widgets.Output()

    def update_summary(ruc, uf, dpto, fecha_inicio_val, fecha_fin_val):
        nonlocal filtro_actual
        output_tabla.clear_output()

        df = BD_RUIAS1.copy()

        if ruc:
            df = df[df['NUM_DOC'].isin(ruc)]
        if uf:
            df = df[df['UF'].isin(uf)]
        if dpto:
            df = df[df['DPTO'].isin(dpto)]
        if fecha_inicio_val and fecha_fin_val:
            df = df[
                (df['F_RESOL_RD'].dt.date >= fecha_inicio_val) &
                (df['F_RESOL_RD'].dt.date <= fecha_fin_val)
            ]

        filtro_actual = df.copy()

        resumen = df.groupby('UF').agg(
            Expedientes=('NUM_EXP', 'nunique'),
            Multas=('MULT_FIN_WEB', 'sum')
        ).reset_index().rename(columns={'UF': 'Unidad Fiscalizable'})

        with output_tabla:
            display(
            resumen.head(20)
            .style
            .hide(axis='index')  # oculta el índice
            .set_table_attributes("style='display:inline-block'")  # presentación
            .set_caption("Mostrando las primeras 20 filas")
                    )

    # --- Interfaz completa ---
    filtros = widgets.VBox([
        widgets.HTML('<h2 style="color:#EF7911;">📊 Tabla resumen de multas por unidad fiscalizable</h2>'),
        widgets.HTML('<h3 style="color:#EF7911;">Filtros</h3>'),
        widgets.HBox([ruc_input]),
        widgets.HBox([ruc_select]),
        widgets.HBox([uf_input]),
        widgets.HBox([uf_select]),
        widgets.HBox([dpto_input]),
        widgets.HBox([dpto_select]),
        widgets.HTML('<h4 style="color:#EF7911;">Fecha de emisión de la resolución de responsabilidad administrativa</h4>'),
        widgets.HBox([fecha_inicio, fecha_fin]),
        boton_descarga,
        output_descarga
    ])

    interactiva = widgets.interactive_output(update_summary, {
        'ruc': ruc_select,
        'uf': uf_select,
        'dpto': dpto_select,
        'fecha_inicio_val': fecha_inicio,
        'fecha_fin_val': fecha_fin
    })

    display(filtros, interactiva, output_tabla)
