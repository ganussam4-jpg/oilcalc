# -*- coding: utf-8 -*-
"""
OILCALC APK — Kivy-приложение для Android.
GUI-обёртка над calc_engine.py. Все формулы — из единого движка.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.popup import Popup

import calc_engine as ce

# Тёмная тема — лучше читается на ярком солнце месторождения
Window.clearcolor = (0.07, 0.09, 0.12, 1)

# Цвета (нефтегаз — янтарный + сталь)
C_BG       = (0.07, 0.09, 0.12, 1)
C_PANEL    = (0.12, 0.15, 0.19, 1)
C_AMBER    = (0.95, 0.65, 0.13, 1)   # янтарный — основные кнопки
C_AMBER_D  = (0.78, 0.50, 0.08, 1)
C_TEXT     = (0.93, 0.94, 0.96, 1)
C_DIM      = (0.62, 0.66, 0.72, 1)
C_OK       = (0.27, 0.78, 0.45, 1)
C_DANGER   = (0.85, 0.30, 0.30, 1)

# Базовые размеры (адаптируются под масштаб)
SCALE = 1.0

def s(x): return dp(x * SCALE)


# ────────────────────── ОПИСАНИЕ РАСЧЁТОВ ──────────────────────
# (label, function_in_engine, [(input_label, key, type, default_or_options)])
# type: float, int, bool, choice
#
# Формулы те же, входы — те же.

CALCS = {
    "Защиты СУ": [
        ("Уставки ЗП и ЗСП (ток / cosφ)", ce.zp_zsp, [
            ("Номинальный ток двигателя, А", "I_nom", "float", None),
            ("cosφ ПЭД (рабочий)",            "cosphi_rab", "float", None),
            ("Рабочий ток ПЭД, А",            "I_rab", "float", None),
            ("Коэффициент трансформации",     "k_tr", "float", None),
            ("cosφ по паспорту",              "cosphi_pasp", "float", None),
        ]),
        ("ЗСП по загрузке ПЭД", ce.zsp_zagruzka, [
            ("Текущая загрузка ПЭД, %",       "zagr_pct", "float", None),
            ("Скважина ВНР/ВНС?",             "is_vnr_vns", "bool", False),
        ]),
        ("Уставки P приёма и T ПЭД", ce.p_t_ustavki, [
            ("Текущее P на приёме, Атм",                          "P_priem", "float", None),
            ("Текущая T ПЭД, °C",                                  "T_rab", "float", None),
            ("Max T группы (Д1=120, Д2=150), °C",                  "T_max_group", "float", 120),
        ]),
        ("Перекос фаз по току", ce.perekos_faz, [
            ("Ток фазы A, А",                 "Ia", "float", None),
            ("Ток фазы B, А",                 "Ib", "float", None),
            ("Ток фазы C, А",                 "Ic", "float", None),
            ("Наименьшее показание тока, А",  "I_min", "float", None),
        ]),
    ],
    "Приток / охлаждение / дебит": [
        ("Дебит по ТОР", ce.debet_tor, [
            ("Время замера в часах (или 1)",   "t_hours", "float", 1),
            ("Время замера в минутах (или 1)", "t_minutes", "float", 1),
            ("Q2 ТОР, м³/сут",                 "Q2", "float", None),
            ("Q1 ТОР, м³/сут",                 "Q1", "float", None),
        ]),
        ("Притоки (герм./негерм. ОК)", ce.pritoki, [
            ("V затруб. кольц. пр-ва 1 п.м., м³",   "V_kolts_pm", "float", None),
            ("V внутр. 1 п.м. НКТ, м³",              "V_nkt_pm", "float", None),
            ("Динуровень 2, м",                       "H_din2", "float", None),
            ("Динуровень 1, м",                       "H_din1", "float", None),
            ("Статуровень в момент окончания слива, м", "H_stat", "float", None),
            ("Время исследования, ч",                  "t_h", "float", None),
        ]),
        ("Средний мгновенный приток за цикл", ce.sredniy_pritok_apv, [
            ("Время слива, мин",                       "t_sliv_min", "float", None),
            ("Время появления подачи на устье, мин",   "t_prikhod_min", "float", None),
            ("S сечения затруб. пр-ва, м²",            "S_zatrub", "float", None),
            ("P на приёме в начале цикла, Атм",         "P_n_atm", "float", None),
            ("P на приёме в конце цикла, Атм",          "P_k_atm", "float", None),
            ("Плотность жидкости, кг/м³",               "rho", "float", 850),
            ("Средний угол наклона ствола, °",          "angle_deg", "float", None),
        ]),
        ("Подача УЭЦН после прихода", ce.podacha_posle_prikhoda, [
            ("Пересч. коэф. НКТ (60=2.83, 73=4.34, 89=6.55)", "k_nkt", "float", 4.34),
            ("Статуровень в затрубе, м",                       "H_stat", "float", None),
            ("Время появления подачи, мин",                    "t_prikhod_min", "float", None),
        ]),
        ("Подача по скорости подъёма в НКТ", ce.podacha_v_nkt, [
            ("V 1 п.м. НКТ (60=2, 73=3, 89=4.5), л", "V_nkt_pm_l", "float", 3),
            ("Замер уровня 2 в НКТ (УГАС), м",        "H2", "float", None),
            ("Время между замерами, ч",                "t_hours", "float", None),
            ("Замер уровня 1 в НКТ, м",                "H1", "float", None),
        ]),
        ("Охлаждение ПЭД по загрузке", ce.pritok_okhl_po_zagruzke, [
            ("Рабочий ток ПЭД, А",                   "I_rab", "float", None),
            ("Номинальный ток ПЭД, А",               "I_nom", "float", None),
            ("Приток для ПЭД при ном. загрузке (табл.), м³/сут", "pritok_nom_tabl", "float", None),
        ]),
        ("Мин. достаточный приток ПЭД", ce.pritok_min_dost, [
            ("Приток при ном. загрузке (табл.), м³/сут",  "pritok_tabl", "float", None),
            ("Рабочий ток ПЭД, А",                         "I_rab", "float", None),
            ("Номинальный ток ПЭД, А",                     "I_nom", "float", None),
            ("S кольц. пр-ва корпус–ЭК, м²",                "S_kolts", "float", None),
            ("Мин. скорость потока (прил.19), м/с",         "v_min", "float", None),
        ]),
    ],
    "Уровни / напор": [
        ("Напор УЭЦН на частоте", ce.napor_na_chastote, [
            ("Частота, Гц",            "f_hz", "float", 50),
            ("Напор по паспорту, м",   "H_pasp", "float", None),
        ]),
        ("Динуровень по ТМС", ce.dinuroven_tms, [
            ("Затрубное P, Атм",       "P_zatrub_atm", "float", None),
            ("P по датчику ТМС, Атм",  "P_tms_atm", "float", None),
            ("Глубина спуска УЭЦН, м", "H_spusk", "float", None),
            ("Плотность жидкости, кг/м³","rho", "float", 850),
        ]),
        ("Приток на охлаждение через АГЗУ/ТМС", ce.pritok_okhl_tms, [
            ("V затруб. кольц. пр-ва, м³",   "V_zatrub", "float", None),
            ("Q по АГЗУ, м³/сут",             "Q_agzu", "float", None),
            ("Статуровень, м",                "H_stat", "float", None),
            ("Время между замерами, ч",       "t_zamer_h", "float", None),
            ("Динуровень, м",                  "H_din", "float", None),
        ]),
        ("Потери напора на трение", ce.potery_napora, [
            ("Скорость течения, м/с",          "v_msec", "float", None),
            ("g (обычно 9.81)",                 "g", "float", 9.81),
            ("Длина трубы, м",                  "L", "float", None),
            ("Диаметр трубы, м",                "D", "float", None),
            ("Плотность жидкости, кг/м³",       "rho", "float", 850),
            ("Шероховатость (новые ст.=0.00005)","eps", "float", 0.00005),
            ("Динамическая вязкость, Па·с",      "mu", "float", 0.001),
        ]),
    ],
    "Кабель / отпайка / мощность": [
        ("Подбор сечения кабеля", ce.kabel_podbor, [
            ("U отпайки по вторич. обмотке ТМПН, В", "U_otp_V", "float", None),
            ("Номинальный ток ПЭД, А",                "I_nom", "float", None),
            ("Допустимый длительный ток (табл.24,25), А", "I_dop", "float", None),
        ]),
        ("Потери мощности в кабеле", ce.kabel_potery_moshnosti, [
            ("S сечения жилы, мм²",                "S_mm2", "float", None),
            ("Длина кабельной линии, м",            "L_m", "float", None),
            ("Удельное сопр. меди (0.01875), Ом·мм²/м","rho_om_mm", "float", 0.01875),
            ("Температура пласта, °C",              "T_plast", "float", None),
            ("Рабочий ток, А",                      "I_rab", "float", None),
        ]),
        ("Отпайка ТМПН (СУ с ЧРП и без)", ce.otpayka_tmpn, [
            ("Фактическое U сети, В",               "U_set", "float", 380),
            ("U ПЭД ном. (паспорт), В",             "U_ped_nom", "float", None),
            ("Ном. ток ПЭД, А",                      "I_ped_nom", "float", None),
            ("Длина кабельной линии, м",             "L_kab_m", "float", None),
            ("S сечения кабеля, мм²",                "S_mm2", "float", None),
            ("Уд. сопр. (медь=0.017, ал=0.026)",     "rho_provod", "float", 0.017),
            ("cosφ ПЭД (асинхр=0.85, вентильн=0.95)","cosphi", "float", 0.85),
            ("T пласта, °C",                          "T_plast", "float", None),
            ("Коэф. сниж. U на фильтре",              "k_filter", "float", 1.0),
            ("Ном. частота ПЭД, Гц",                  "f_ped_nom", "float", 50),
            ("Макс. вх. частота ЧРП, Гц",              "f_chrp_max", "float", 60),
            ("Ном. вх. U ТМПН, В",                    "U_tmpn_nom", "float", 380),
            ("Допустимый длительный ток (табл.), А",  "I_dop", "float", None),
        ]),
        ("Потребляемая мощность УЭЦН", ce.moshchnost_potr, [
            ("U ТМПН, В",                  "U_tmpn", "float", None),
            ("Рабочий ток ПЭД, А",          "I_rab", "float", None),
            ("cosφ ПЭД",                    "cosphi", "float", 0.85),
            ("Вых. U СУ, В",                "U_su_out", "float", None),
            ("Ном. U сети, В",              "U_set_nom", "float", 380),
        ]),
        ("Электроэнергия УЭЦН (сутки/мес/удел.)", ce.energy_uec, [
            ("U ТМПН, В",                  "U_tmpn", "float", None),
            ("Рабочий ток ПЭД, А",          "I_rab", "float", None),
            ("cosφ ПЭД",                    "cosphi", "float", 0.85),
            ("Вых. U СУ, В",                "U_su_out", "float", None),
            ("Ном. U сети, В",              "U_set_nom", "float", 380),
            ("Время работы за сутки, ч",    "t_work_h_day", "float", 24),
            ("Дебит жидкости, м³/сут",      "Q_zhid", "float", None),
        ]),
    ],
    "ПРГ / АПВ": [
        ("Расчёт ПРГ", ce.prg, [
            ("Внутр. диам. ЭК, м",                          "D_ek", "float", None),
            ("Наружн. диам. НКТ, м",                         "D_nkt", "float", None),
            ("Плотность пласт. нефти, кг/м³",                "rho_oil", "float", 850),
            ("Плотность пласт. воды, кг/м³",                  "rho_water", "float", 1010),
            ("Обводнение, %",                                  "water_cut_pct", "float", None),
            ("Приток для проектного P забоя, м³/сут",         "pritok_proj", "float", None),
            ("Расч. подача насоса в раб. период, м³/сут",     "podacha", "float", None),
            ("Проектное P на приёме, Атм",                    "P_priem_proj_atm", "float", None),
            ("Время работы УЭЦН, мин",                         "t_work_min", "float", None),
            ("Время накопления, мин",                          "t_acc_min", "float", None),
            ("Плотность жидкости, кг/м³",                      "rho_zhid", "float", 850),
        ]),
        ("Цикл АПВ-2 (средняя мощность)", ce.apv2, [
            ("Рассчитанная мощность установки, кВт",          "power_kw", "float", None),
            ("Приток для проектного P, м³/сут",                "pritok_proj", "float", None),
            ("Время разгона ЧП, с",                            "t_razgon_sec", "float", None),
            ("Расч. подача насоса, м³/сут",                    "podacha", "float", None),
            ("Время цикла",                                     "t_cycle", "float", None),
        ]),
    ],
    "Газ / сепарация": [
        ("Содержание свободного газа на входе", ce.soderzh_gaza, [
            ("Объёмн. коэф. жидкости (60=2.83, 73=4.34, 89=6.55)","k_nkt", "float", 4.34),
            ("Дебит жидкости на поверхности, м³/сут",              "Q_zhid_surf", "float", None),
            ("S сечения скважины на приёме, м²",                    "S_priem", "float", None),
            ("V всплытия пузырьков (B<50%=0.02; ≥50%=0.16) см/с",   "V_pyz_sms", "float", 0.02),
            ("P на приёме, Атм",                                    "P_priem_atm", "float", None),
            ("P насыщения, Атм",                                    "P_nasys_atm", "float", None),
            ("Текущий газовый фактор",                              "gaz_faktor", "float", None),
        ]),
        ("Учёт влияния газа (сепарация)", ce.uchet_gaza, [
            ("Коэф. естеств. сепарации, доли",        "k_nat_sep", "float", None),
            ("Коэф. газосепаратора, доли (по умолч. 0.5)", "k_gas_sep", "float", 0.5),
            ("Общ. V свободного газа на приёме, м³",    "V_gas_total", "float", None),
            ("Замер дебита газа (ПЗУ/АГЗУ), м³",         "Q_gas_meas", "float", None),
            ("Замер дебита нефти (ПЗУ/АГЗУ), м³",        "Q_oil_meas", "float", None),
        ]),
    ],
    "Геометрия / промывка": [
        ("Площадь кольцевого пр-ва", ce.ploshchad_kolts, [
            ("Внутр. диам. ЭК на глубине ПЭД, мм", "D_ek_mm", "float", None),
            ("Наружн. диам. ПЭД, мм",              "D_ped_mm", "float", None),
        ]),
        ("Нулевой изгиб в интервале спуска", ce.izgib_uec, [
            ("Внутр. диам. ЭК, мм",          "D_ek_mm", "float", None),
            ("Макс. габарит установки, мм",  "D_max_uec_mm", "float", None),
            ("Длина установки, м",            "L_uec_m", "float", None),
        ]),
        ("Минимальный объём промывки", ce.promyvka_obem, [
            ("Внутр. диам. ЭК, мм",   "D_ek_mm", "float", None),
            ("Наружн. диам. НКТ, мм", "D_nkt_mm", "float", None),
            ("Статический уровень, м","H_stat", "float", None),
        ]),
    ],
    "Конвертер единиц": [],  # см. отдельный экран ниже
}


# ────────── Конвертер: коэффициенты в SI ──────────
CONVERTERS = {
    "Давление": {
        "Атм (физ.)": 101325.0, "кгс/см² (техн.атм.)": 98066.5, "бар": 100000.0,
        "МПа": 1_000_000.0, "кПа": 1000.0, "psi": 6894.757293168, "мм рт.ст.": 133.322387415,
    },
    "Длина": {
        "м": 1.0, "км": 1000.0, "фут": 0.3048, "дюйм": 0.0254, "ярд": 0.9144, "миля": 1609.344,
    },
    "Объём": {
        "м³": 1.0, "литр": 0.001, "баррель (нефт. US)": 0.158987294928,
        "галлон US": 0.003785411784, "фут³": 0.028316846592,
    },
    "Дебит": {
        "м³/сут": 1.0, "м³/час": 24.0, "bbl/сут": 0.158987294928, "л/мин": 60*24/1000.0,
    },
    "Мощность": {
        "Вт": 1.0, "кВт": 1000.0, "л.с. (HP)": 745.6998715822702, "л.с. (метрич.)": 735.49875,
    },
    "Вязкость дин.": {"Па·с": 1.0, "сП (мПа·с)": 0.001},
    "Вязкость кин.": {"м²/с": 1.0, "сСт (мм²/с)": 1e-6},
}


# ───────────────────────── ВИДЖЕТЫ ─────────────────────────

def big_button(text, on_press, color=C_AMBER, height=72):
    b = Button(
        text=text, size_hint_y=None, height=s(height),
        background_normal="", background_color=color,
        color=(0.07, 0.09, 0.12, 1), bold=True, font_size=s(18),
    )
    b.bind(on_release=on_press)
    return b

def section_label(text):
    return Label(
        text=text, size_hint_y=None, height=s(50),
        color=C_AMBER, bold=True, font_size=s(22), halign="left",
        text_size=(Window.width - s(20), None),
    )

def small_label(text, color=C_TEXT):
    lbl = Label(
        text=text, size_hint_y=None, height=s(34),
        color=color, font_size=s(15), halign="left", valign="middle",
    )
    lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    return lbl


# ───────────────────────── ЭКРАНЫ ─────────────────────────

class HomeScreen(Screen):
    """Главное меню разделов."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=s(12), spacing=s(8))

        # шапка
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=s(80))
        header.add_widget(Label(
            text="[b]OILCALC[/b]", markup=True,
            color=C_AMBER, font_size=s(28), size_hint_y=None, height=s(40)))
        header.add_widget(Label(
            text="Полевой калькулятор технолога УЭЦН",
            color=C_DIM, font_size=s(14), size_hint_y=None, height=s(28)))
        root.add_widget(header)

        # сетка разделов
        sv = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=s(8), padding=(0, s(4)))
        grid.bind(minimum_height=grid.setter("height"))

        for section in CALCS.keys():
            grid.add_widget(big_button(section, self._on_section(section), height=78))

        sv.add_widget(grid)
        root.add_widget(sv)

        # нижняя панель
        bottom = BoxLayout(orientation="horizontal", size_hint_y=None, height=s(56), spacing=s(8))
        bottom.add_widget(big_button("A−", self._scale_down, color=C_PANEL, height=56))
        bottom.add_widget(big_button("A+", self._scale_up, color=C_PANEL, height=56))
        bottom.add_widget(big_button("О программе", self._about, color=C_PANEL, height=56))
        root.add_widget(bottom)

        self.add_widget(root)

    def _on_section(self, section_name):
        def handler(*_):
            self.manager.transition = SlideTransition(direction="left")
            scr = self.manager.get_screen("section")
            scr.show_section(section_name)
            self.manager.current = "section"
        return handler

    def _scale_up(self, *_):
        global SCALE
        SCALE = min(SCALE + 0.2, 2.0)
        rebuild_all(self.manager)

    def _scale_down(self, *_):
        global SCALE
        SCALE = max(SCALE - 0.2, 0.8)
        rebuild_all(self.manager)

    def _about(self, *_):
        Popup(
            title="О программе",
            content=Label(text=(
                "OILCALC v1.0\n\n"
                "Полевой калькулятор технолога\n"
                "по добыче нефти (УЭЦН).\n\n"
                "Все формулы — из регламента\n"
                "пользователя. Без интернета.\n\n"
                "A+/A− — масштаб шрифта."
            ), color=C_TEXT, font_size=s(16)),
            size_hint=(0.85, 0.55),
        ).open()


class SectionScreen(Screen):
    """Список расчётов внутри раздела."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.container = None
        self._build_shell()

    def _build_shell(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=s(12), spacing=s(8))
        self.title_lbl = Label(
            text="", color=C_AMBER, font_size=s(22), bold=True,
            size_hint_y=None, height=s(46), halign="left",
            text_size=(Window.width - s(20), None),
        )
        root.add_widget(self.title_lbl)
        self.sv = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=s(8))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.sv.add_widget(self.grid)
        root.add_widget(self.sv)
        root.add_widget(big_button("← Назад", self._back, color=C_PANEL, height=56))
        self.add_widget(root)

    def show_section(self, name):
        self.section_name = name
        self.title_lbl.text = name
        self.grid.clear_widgets()
        if name == "Конвертер единиц":
            for conv_name in CONVERTERS.keys():
                self.grid.add_widget(big_button(conv_name, self._open_conv(conv_name), height=70))
            return
        for i, (label, fn, fields) in enumerate(CALCS[name]):
            self.grid.add_widget(big_button(label, self._open_calc(i), height=70))

    def _open_calc(self, idx):
        def handler(*_):
            scr = self.manager.get_screen("calc")
            scr.show_calc(self.section_name, idx)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "calc"
        return handler

    def _open_conv(self, conv_name):
        def handler(*_):
            scr = self.manager.get_screen("conv")
            scr.show_conv(conv_name)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "conv"
        return handler

    def _back(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


class CalcScreen(Screen):
    """Экран ввода данных + вывод результата."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.inputs = {}
        self._build_shell()

    def _build_shell(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=s(12), spacing=s(6))
        self.title_lbl = Label(
            text="", color=C_AMBER, font_size=s(20), bold=True,
            size_hint_y=None, height=s(44), halign="left",
            text_size=(Window.width - s(20), None),
        )
        root.add_widget(self.title_lbl)

        self.sv = ScrollView()
        self.form = GridLayout(cols=1, size_hint_y=None, spacing=s(4))
        self.form.bind(minimum_height=self.form.setter("height"))
        self.sv.add_widget(self.form)
        root.add_widget(self.sv)

        # кнопки
        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=s(60), spacing=s(8))
        btn_row.add_widget(big_button("← Назад", self._back, color=C_PANEL, height=60))
        btn_row.add_widget(big_button("РАССЧИТАТЬ", self._calculate, color=C_AMBER, height=60))
        root.add_widget(btn_row)

        # результаты
        self.result_box = BoxLayout(orientation="vertical", size_hint_y=None, height=0, spacing=s(2))
        root.add_widget(self.result_box)

        self.add_widget(root)

    def show_calc(self, section, idx):
        self.section = section
        self.idx = idx
        label, self.fn, fields = CALCS[section][idx]
        self.fields = fields
        self.title_lbl.text = label
        self.form.clear_widgets()
        self.inputs = {}
        self.result_box.clear_widgets()
        self.result_box.height = 0

        for fld in fields:
            flabel, key, ftype, default = fld
            self.form.add_widget(small_label(flabel, color=C_TEXT))
            if ftype == "bool":
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=s(48), spacing=s(8))
                state = {"value": bool(default)}
                def make_toggle(s_dict, btn_yes, btn_no):
                    def t_yes(*_):
                        s_dict["value"] = True
                        btn_yes.background_color = C_AMBER
                        btn_no.background_color = C_PANEL
                    def t_no(*_):
                        s_dict["value"] = False
                        btn_yes.background_color = C_PANEL
                        btn_no.background_color = C_AMBER
                    return t_yes, t_no
                btn_yes = Button(text="да", background_normal="", color=C_TEXT, font_size=s(16))
                btn_no  = Button(text="нет", background_normal="", color=C_TEXT, font_size=s(16))
                t_yes, t_no = make_toggle(state, btn_yes, btn_no)
                btn_yes.bind(on_release=t_yes)
                btn_no.bind(on_release=t_no)
                btn_no.background_color = C_AMBER  # дефолт "нет"
                btn_yes.background_color = C_PANEL
                if default:
                    t_yes()
                row.add_widget(btn_yes); row.add_widget(btn_no)
                self.form.add_widget(row)
                self.inputs[key] = ("bool", state)
            else:
                ti = TextInput(
                    text=str(default) if default is not None else "",
                    multiline=False, input_filter="float" if ftype == "float" else "int",
                    size_hint_y=None, height=s(48), font_size=s(18),
                    background_color=C_PANEL, foreground_color=C_TEXT, cursor_color=C_AMBER,
                    padding=[s(10), s(12), s(10), s(12)],
                )
                self.form.add_widget(ti)
                self.inputs[key] = (ftype, ti)

    def _calculate(self, *_):
        kwargs = {}
        try:
            for key, (ftype, src) in self.inputs.items():
                if ftype == "bool":
                    kwargs[key] = src["value"]
                else:
                    raw = src.text.strip().replace(",", ".")
                    if raw == "":
                        raise ValueError(f"Заполните: {key}")
                    kwargs[key] = float(raw) if ftype == "float" else int(raw)
            result = self.fn(**kwargs)
        except Exception as e:
            self._show_error(str(e))
            return
        self._show_result(result)

    def _show_result(self, result):
        self.result_box.clear_widgets()
        rows = list(result.items())
        # высота: заголовок + (название + значение) на каждую строку
        h = s(40) + sum(s(56) for _ in rows)
        self.result_box.height = h

        hdr = Label(text="РЕЗУЛЬТАТ", color=C_AMBER, bold=True,
                    font_size=s(16), size_hint_y=None, height=s(40))
        self.result_box.add_widget(hdr)

        for label, value in rows:
            row = BoxLayout(orientation="vertical", size_hint_y=None, height=s(56), spacing=s(2))
            name_lbl = Label(
                text=label, color=C_DIM, font_size=s(13),
                size_hint_y=None, height=s(22), halign="left",
                text_size=(Window.width - s(30), None),
            )
            if isinstance(value, float):
                vs = f"{value:.4f}".rstrip("0").rstrip(".")
            else:
                vs = str(value)
            val_lbl = Label(
                text=vs, color=C_OK, bold=True, font_size=s(22),
                size_hint_y=None, height=s(32), halign="left",
                text_size=(Window.width - s(30), None),
            )
            row.add_widget(name_lbl); row.add_widget(val_lbl)
            self.result_box.add_widget(row)

    def _show_error(self, msg):
        Popup(title="Ошибка", content=Label(text=msg, color=C_DANGER),
              size_hint=(0.8, 0.4)).open()

    def _back(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "section"


class ConvScreen(Screen):
    """Конвертер единиц."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_shell()

    def _build_shell(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=s(12), spacing=s(6))
        self.title_lbl = Label(text="", color=C_AMBER, font_size=s(20), bold=True,
                                size_hint_y=None, height=s(44), halign="left",
                                text_size=(Window.width - s(20), None))
        root.add_widget(self.title_lbl)

        # поле ввода
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=s(56), spacing=s(8))
        self.value_input = TextInput(
            text="1", multiline=False, input_filter="float",
            font_size=s(18), background_color=C_PANEL, foreground_color=C_TEXT,
            cursor_color=C_AMBER, padding=[s(10), s(14), s(10), s(14)],
        )
        self.value_input.bind(text=lambda *_: self._recalc())
        row.add_widget(self.value_input)
        root.add_widget(row)

        # выбор «из»
        self.from_label = small_label("Из единицы:", C_DIM)
        root.add_widget(self.from_label)
        self.from_grid = GridLayout(cols=2, size_hint_y=None, spacing=s(4))
        self.from_grid.bind(minimum_height=self.from_grid.setter("height"))
        root.add_widget(self.from_grid)

        # результаты
        root.add_widget(small_label("В единицы:", C_DIM))
        self.sv = ScrollView()
        self.results = GridLayout(cols=1, size_hint_y=None, spacing=s(2))
        self.results.bind(minimum_height=self.results.setter("height"))
        self.sv.add_widget(self.results)
        root.add_widget(self.sv)

        root.add_widget(big_button("← Назад", self._back, color=C_PANEL, height=56))
        self.add_widget(root)

    def show_conv(self, conv_name):
        self.conv_name = conv_name
        self.title_lbl.text = f"Конвертер: {conv_name}"
        self.units = CONVERTERS[conv_name]
        self.from_unit = list(self.units.keys())[0]
        self._rebuild_from_buttons()
        self._recalc()

    def _rebuild_from_buttons(self):
        self.from_grid.clear_widgets()
        for u in self.units.keys():
            color = C_AMBER if u == self.from_unit else C_PANEL
            text_color = (0.07, 0.09, 0.12, 1) if u == self.from_unit else C_TEXT
            btn = Button(
                text=u, size_hint_y=None, height=s(46),
                background_normal="", background_color=color,
                color=text_color, font_size=s(14),
            )
            btn.bind(on_release=self._set_from(u))
            self.from_grid.add_widget(btn)

    def _set_from(self, u):
        def h(*_):
            self.from_unit = u
            self._rebuild_from_buttons()
            self._recalc()
        return h

    def _recalc(self):
        self.results.clear_widgets()
        try:
            v = float((self.value_input.text or "0").replace(",", "."))
        except ValueError:
            return
        si = v * self.units[self.from_unit]
        rows = [(k, si / coef) for k, coef in self.units.items() if k != self.from_unit]
        self.results.height = sum(s(48) for _ in rows)
        for name, val in rows:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=s(48), spacing=s(8))
            row.add_widget(Label(text=name, color=C_DIM, font_size=s(14),
                                  halign="left", text_size=(Window.width*0.5, None)))
            vs = f"{val:.6g}"
            row.add_widget(Label(text=vs, color=C_OK, bold=True, font_size=s(18),
                                  halign="right", text_size=(Window.width*0.4, None)))
            self.results.add_widget(row)

    def _back(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "section"


# ───────── Перерисовать все экраны при изменении масштаба ─────────
def rebuild_all(manager):
    for name in ("home", "section", "calc", "conv"):
        scr = manager.get_screen(name)
        if name == "home":
            scr.clear_widgets(); scr.build_ui()
        elif name == "section":
            scr._build_shell()
            if hasattr(scr, "section_name"):
                scr.show_section(scr.section_name)
        elif name == "calc":
            scr._build_shell()
        elif name == "conv":
            scr._build_shell()
            if hasattr(scr, "conv_name"):
                scr.show_conv(scr.conv_name)


# ───────────────────────── ЗАПУСК ─────────────────────────

class OilCalcApp(App):
    title = "OILCALC"

    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SectionScreen(name="section"))
        sm.add_widget(CalcScreen(name="calc"))
        sm.add_widget(ConvScreen(name="conv"))
        return sm

    def on_start(self):
        # системная кнопка "Назад" Android — возврат к предыдущему экрану
        Window.bind(on_keyboard=self._on_key)

    def _on_key(self, window, key, *args):
        if key == 27:  # ESC / back
            sm = self.root
            if sm.current == "calc":
                sm.transition = SlideTransition(direction="right")
                sm.current = "section"
                return True
            if sm.current == "conv":
                sm.transition = SlideTransition(direction="right")
                sm.current = "section"
                return True
            if sm.current == "section":
                sm.transition = SlideTransition(direction="right")
                sm.current = "home"
                return True
        return False


if __name__ == "__main__":
    OilCalcApp().run()
