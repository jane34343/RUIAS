
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import io
import base64

def mostrar_interfaz(BD_PAS):
    etapa_a_estado_aux = {
        "ELEVADO AL TFA": "APELACION",
        "CAUTELAR": "CAUTELAR",
        "CONCLUIDO": "CONCLUIDO",
        "DEVUELTO A ÁREA": "DEVUELTO A ÁREA",
        "EN ANALISIS DE INICIO": "EN EVALUCIÓN DE LA AUTORIDAD INSTRUCTORA",
        "NULIDAD DE DICTADO DE MC": "EN TRÁMITE POR NULIDAD",
        "NULIDAD MULTA": "EN TRÁMITE POR NULIDAD",
        "NULIDAD RECONSIDERACIÓN": "EN TRÁMITE POR NULIDAD",
        "NULIDAD RESPONSAB. Y MULTA": "EN TRÁMITE POR NULIDAD",
        "NULIDAD RESPONSABILIDAD": "EN TRÁMITE POR NULIDAD",
        "EVALUACIÓN PENDIENTE": "EVALUACIÓN PENDIENTE",
        "INICIADO": "INICIADO",
        "INICIADO IFI-R": "PAS PENDIENTE DE RESOLUCIÓN",
        "RECONSIDERADO": "RECONSIDERADO",
        "SUSPENDIDO": "SUSPENDIDO"
    }

    BD_PAS["ESTADO_AUX"] = BD_PAS["ETAPA"].map(etapa_a_estado_aux)
    BD_PAS['INICIO DE SUPERVISION'] = pd.to_datetime(BD_PAS['INICIO DE SUPERVISION'], errors='coerce')
    BD_PAS['RUC'] = BD_PAS['RUC'].astype(str)

    estados_filtrar = [
        "CONCLUIDO",
        "EN EVALUCIÓN DE LA AUTORIDAD INSTRUCTORA",
        "EN TRÁMITE POR NULIDAD",
        "INICIADO",
        "PAS PENDIENTE DE RESOLUCIÓN",
        "RECONSIDERADO"
    ]

    BD_PAS = BD_PAS[BD_PAS["ESTADO_AUX"].isin(estados_filtrar)]

    filtro_actual = pd.DataFrame()

    ruc_input = widgets.Text(placeholder='Buscar RUC...', description='Buscar RUC:')
    ruc_select = widgets.SelectMultiple(
        options=sorted(BD_PAS['RUC'].dropna().unique().tolist()),
        description='RUC:',
        rows=6,
        style={'description_width': 'initial'}
    )

    def actualizar_ruc(change):
        texto = change['new']
        opciones = sorted(BD_PAS['RUC'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [r for r in opciones if texto.lower() in str(r).lower()]
            ruc_select.options = filtradas[:100]
        else:
            ruc_select.options = opciones[:100]

    ruc_input.observe(actualizar_ruc, names='value')

    uf_input = widgets.Text(placeholder='Buscar UF...', description='Unidad Fiscalizable:')
    uf_select = widgets.SelectMultiple(
        options=sorted(BD_PAS['UNIDAD FISCALIZABLE'].dropna().unique().tolist()),
        description='UF:',
        rows=6,
        style={'description_width': 'initial'}
    )

    def actualizar_uf(change):
        texto = change['new']
        opciones = sorted(BD_PAS['UNIDAD FISCALIZABLE'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [u for u in opciones if texto.lower() in str(u).lower()]
            uf_select.options = filtradas[:100]
        else:
            uf_select.options = opciones[:100]

    uf_input.observe(actualizar_uf, names='value')

    dpto_input = widgets.Text(placeholder='Buscar Departamento...', description='Departamento:')
    dpto_select = widgets.SelectMultiple(
        options=sorted(BD_PAS['DEPARTAMENTO'].dropna().unique().tolist()),
        description='Departamento:',
        rows=6,
        style={'description_width': 'initial'}
    )

    def actualizar_dpto(change):
        texto = change['new']
        opciones = sorted(BD_PAS['DEPARTAMENTO'].dropna().unique().tolist())
        if len(texto) >= 2:
            filtradas = [d for d in opciones if texto.lower() in str(d).lower()]
            dpto_select.options = filtradas[:100]
        else:
            dpto_select.options = opciones[:100]

    dpto_input.observe(actualizar_dpto, names='value')

    fecha_min = BD_PAS['INICIO DE SUPERVISION'].min().date()
    fecha_max = BD_PAS['INICIO DE SUPERVISION'].max().date()

    fecha_inicio = widgets.DatePicker(description='Desde:', value=fecha_min, style={'description_width': 'initial'})
    fecha_fin = widgets.DatePicker(description='Hasta:', value=fecha_max, style={'description_width': 'initial'})

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

    output_tabla = widgets.Output()

    def update_summary(ruc, uf, dpto, fecha_inicio_val, fecha_fin_val):
        nonlocal filtro_actual
        output_tabla.clear_output()
        df = BD_PAS.copy()

        if ruc:
            df = df[df['RUC'].isin(ruc)]
        if uf:
            df = df[df['UNIDAD FISCALIZABLE'].isin(uf)]
        if dpto:
            df = df[df['DEPARTAMENTO'].isin(dpto)]
        if fecha_inicio_val and fecha_fin_val:
            df = df[
                (df['INICIO DE SUPERVISION'].dt.date >= fecha_inicio_val) &
                (df['INICIO DE SUPERVISION'].dt.date <= fecha_fin_val)
            ]

        filtro_actual = df.copy()

        resumen = pd.pivot_table(
            df,
            index='ADMINISTRADO',
            columns='ESTADO_AUX',
            values='ITEM',
            aggfunc='nunique',
            fill_value=0,
            margins=True,
            margins_name='Total'
        ).reset_index()

        with output_tabla:
            display(HTML('<h3 style="color:#E83670;">Tabla resumen</h3>'))
            display(resumen)

    filtros = widgets.VBox([
        widgets.HTML('<h2 style="color:#E83670;">📊 Tabla resumen por administrado</h2>'),
        widgets.HTML('<h3 style="color:#E83670;"> Filtros  </h3>'),
        widgets.HBox([ruc_input, ruc_select]),
        widgets.HBox([uf_input, uf_select]),
        widgets.HBox([dpto_input, dpto_select]),
        widgets.HTML('<h3 style="color:#E83670;"> La fecha corresponde al inicio de supervisión </h3>'),
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
