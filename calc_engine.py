# -*- coding: utf-8 -*-
"""
OILCALC — чистый расчётный движок (без UI).
Все формулы 1:1 из исходных Python-скриптов пользователя.
Используется и Termux-версией (через тонкий адаптер), и Kivy/APK-версией.
"""
import math


# ──────────────────────────── ЗАЩИТЫ СУ ────────────────────────────

def zp_zsp(I_nom, cosphi_rab, I_rab, k_tr, cosphi_pasp):
    """Уставки ЗП и ЗСП. Источник: зпзсп.py"""
    w = 1.1
    return {
        "ЗП для СУ без контроллера (А)":            I_nom / k_tr,
        "ЗП для СУ с МП-управлением и ПКИ (А)":      w * I_nom,
        "ЗП для REDA/Centrilift без ПКИ (А)":         I_nom,
        "ЗСП по коэф. мощности (%)":                  (I_rab * cosphi_pasp) / (I_nom * cosphi_rab) * 100,
    }


def zsp_zagruzka(zagr_pct, is_vnr_vns):
    """ЗСП по загрузке ПЭД. Источник: настрзсппозагрузке.py"""
    q = zagr_pct
    if is_vnr_vns:
        return {"ЗСП по загрузке (ВНР/ВНС) (%)": q - 15}
    if q >= 70:
        return {"ЗСП по загрузке (≥70 %) (%)": q * 0.88}
    if 50 <= q < 70:
        return {"ЗСП по загрузке (50…70 %) (%)": q * 0.92}
    return {"ЗСП по загрузке (<50 %) (%)": q * 0.95}


def p_t_ustavki(P_priem, T_rab, T_max_group):
    """Уставки P приёма и T ПЭД. Источник: миндавлениемакстемпер.py"""
    i = T_max_group * 0.85
    o = T_rab * 1.15
    if P_priem < 30:
        P_ust = P_priem - (P_priem * 10 / 100)
    else:
        P_ust = P_priem - (P_priem * 15 / 100)
    res = {"Уставка P на приёме насоса (Атм)": P_ust}
    if o > i:
        res["Уставка по температуре ПЭД (°C)"] = i
    else:
        res["Текущий запас по температуре в норме (T·1.15, °C)"] = o
    return res


def perekos_faz(Ia, Ib, Ic, I_min):
    """Перекос фаз по току. Источник: перекосфаз.py"""
    avg = (Ia + Ib + Ic) / 3
    return {
        "Средний ток по 3 фазам (А)": avg,
        "Перекос фаз по току (%)":     (avg - I_min) / avg * 100,
    }


# ─────────────────── ПРИТОК / ОХЛАЖДЕНИЕ / ДЕБИТ ────────────────────

def pritok_okhl_po_zagruzke(I_rab, I_nom, pritok_nom_tabl):
    """Источник: Притокна_охаждениепэдпозагрузке.py"""
    return {"Приток для охлаждения ПЭД (м³/сут)":
            (pritok_nom_tabl * (I_rab ** 2)) / (I_nom ** 2)}


def pritok_min_dost(pritok_tabl, I_rab, I_nom, S_kolts, v_min):
    """Источник: притокпозагрузкеминдостприток.py"""
    return {
        "Мин. достаточный приток (геометрия+V_min) (м³/сут)": S_kolts * v_min * 86400,
        "Приток для охлаждения при загрузке < ном. (м³/сут)":  (pritok_tabl * I_rab ** 2) / I_nom ** 2,
    }


def pritoki(V_kolts_pm, V_nkt_pm, H_din2, H_din1, H_stat, t_h):
    """Источник: притоки.py"""
    dH = H_din2 - H_din1
    return {
        "При герметичном ОК (м³/сут)":                            (dH * V_kolts_pm * 24) / t_h,
        "При негерметичном ОК (м³/сут)":                          (((dH * V_kolts_pm) - (V_nkt_pm * H_stat)) * 24) / t_h,
        "При негерм./отсутств. ОК (после слива НКТ) (м³/сут)":   (dH * (V_nkt_pm + V_kolts_pm) * 24) / t_h,
    }


def sredniy_pritok_apv(t_sliv_min, t_prikhod_min, S_zatrub, P_n_atm, P_k_atm, rho, angle_deg):
    """Источник: среднийпритокапв.py"""
    dP = P_n_atm - P_k_atm
    g = 9.81
    cosv = math.cos(angle_deg * math.pi / 180)
    o = (S_zatrub * dP) / (rho * g * t_sliv_min * cosv)
    return {"Средний мгновенный приток за цикл накопления (усл. ед.)": o}


def debet_tor(t_hours, t_minutes, Q2, Q1):
    """Источник: расчётдебитапотору.py"""
    t = Q2 - Q1
    return {
        "Дебит (если время в часах) (м³/час)": t / t_hours * 24,
        "Дебит (если время в минутах) (—)":    t / t_minutes * 1440,
    }


def podacha_posle_prikhoda(k_nkt, H_stat, t_prikhod_min):
    """Источник: расчетподачи.py"""
    return {"Подача УЭЦН после прихода на устье (м³/сут)": (H_stat * k_nkt) / t_prikhod_min}


def podacha_v_nkt(V_nkt_pm_l, H2, t_hours, H1):
    """Источник: подачауэцнпоскорподъема_жидкостивнкт.py"""
    dH = H2 - H1
    return {"Подача по скорости подъёма жидкости в НКТ (м³/сут)":
            (V_nkt_pm_l * dH * 24) / (1000 * t_hours)}


# ────────────────────── УРОВНИ / НАПОР ──────────────────────

def napor_na_chastote(f_hz, H_pasp):
    """Источник: напорпритокдинуровеньподатчику.py"""
    return {"Напор УЭЦН на частоте (м)": ((f_hz / 50) ** 2) * H_pasp}


def dinuroven_tms(P_zatrub_atm, P_tms_atm, H_spusk, rho):
    """Источник: напорпритокдинуровеньподатчику.py"""
    return {"Динамический уровень (м)":
            H_spusk - (((P_tms_atm - P_zatrub_atm) * 98.07) / (rho * 9.81))}


def pritok_okhl_tms(V_zatrub, Q_agzu, H_stat, t_zamer_h, H_din):
    """Источник: напорпритокдинуровеньподатчику.py"""
    o = H_din - H_stat
    return {"Приток для охлаждения (АГЗУ ± изменение уровня) (м³/сут)":
            Q_agzu - ((o * V_zatrub * 24) / t_zamer_h)}


def potery_napora(v_msec, g, L, D, rho, eps, mu):
    """Источник: потеринапоранатрение.py"""
    p = rho * v_msec * (D / mu)
    u = 0.1 * 1.46 * ((eps / D) + (100 / p))
    return {"Потери напора на гидравлическом сопротивлении (м)":
            u * (L / g) * (v_msec ** 2) / (2 * g)}


# ────────────── КАБЕЛЬ / ОТПАЙКА / МОЩНОСТЬ ──────────────

def kabel_podbor(U_otp_V, I_nom, I_dop):
    """Источник: подборсечениякабеля.py"""
    w = 1.1
    r = U_otp_V / 380 * I_nom * w
    return {
        "Расчётный ток кабельной линии НН (А)": r,
        "Количество ниток кабеля (НН-линия)":   r / I_dop,
    }


def kabel_potery_moshnosti(S_mm2, L_m, rho_om_mm, T_plast, I_rab):
    """Источник: потеримощностивкабеле.py"""
    t = 0.79
    y = 0.0043
    i = rho_om_mm * (L_m / S_mm2)
    o = (I_rab * t) + T_plast
    p = i * (1 + (y * (o - 20)))
    return {
        "Сопротивление кабеля при рабочей T (Ом)":  p,
        "Потери активной мощности в кабеле (кВт)": 3 * (I_rab ** 2) * (p / 1000),
    }


def otpayka_tmpn(U_set, U_ped_nom, I_ped_nom, L_kab_m, S_mm2, rho_provod,
                 cosphi, T_plast, k_filter, f_ped_nom, f_chrp_max, U_tmpn_nom, I_dop):
    """Источник: расчетотпайкиподборкабеля.py (√3 исправлено на math.sqrt(3))"""
    h = 1 + 0.0043 * (T_plast - 20)
    e = math.sqrt(3) * I_ped_nom * cosphi * (1000 / S_mm2) * rho_provod * h
    n = (380 / U_ped_nom * (f_chrp_max / f_ped_nom) * U_ped_nom * k_filter) + e
    b = (U_tmpn_nom / U_set * U_ped_nom) + e
    v = b / 380 * I_ped_nom * 1.1
    qw = n / 380 * I_ped_nom * 1.1
    return {
        "Отпайка для СУ без ЧРП (В)":                       b,
        "Текущая отпайка для СУ с ЧРП (В)":                 n,
        "Кол-во ниток кабеля (СУ без ЧРП)":                 v / I_dop,
        "Кол-во ниток кабеля (СУ с ЧРП)":                   qw / I_dop,
    }


def moshchnost_potr(U_tmpn, I_rab, cosphi, U_su_out, U_set_nom):
    """Источник: потрмощнэцн.py (√3 исправлено)"""
    return {"Потребляемая мощность УЭЦН (кВт·ч)":
            math.sqrt(3) * U_tmpn * cosphi * (U_su_out / U_set_nom / 1000)}


def energy_uec(U_tmpn, I_rab, cosphi, U_su_out, U_set_nom, t_work_h_day, Q_zhid):
    """Источник: элэнергияУЭЦН.py (√3 исправлено)"""
    o_month_hours = t_work_h_day * 24 * 30
    P = math.sqrt(3) * U_tmpn * cosphi * (U_su_out / U_set_nom / 1000)
    return {
        "Потребляемая мощность УЭЦН (кВт·ч)":      P,
        "Удельное потребление на 1 м³ (кВт·ч/м³)": P * t_work_h_day / Q_zhid,
        "Энергопотребление за месяц (кВт·мес)":     P * (o_month_hours / 1000),
    }


# ────────────────── ПРГ / АПВ / ПЕРИОДИКА ──────────────────

def prg(D_ek, D_nkt, rho_oil, rho_water, water_cut_pct, pritok_proj,
        podacha, P_priem_proj_atm, t_work_min, t_acc_min, rho_zhid):
    """Источник: расчетпргупр.py"""
    p = (podacha - pritok_proj) / 1440 * t_work_min
    a = (p * 1440) / pritok_proj
    d = t_work_min * (t_acc_min / a)
    j = D_ek * rho_zhid * 9.81 / 101300
    z = P_priem_proj_atm - j
    return {
        "Время работы цикла (мин)":                       d,
        "Время накопления цикла (мин)":                   a,
        "Уставка P на приёме для отключения (Атм)":        z,
        "Уставка P для запуска установки (Атм)":           P_priem_proj_atm,
    }


def apv2(power_kw, pritok_proj, t_razgon_sec, podacha, t_cycle):
    """Источник: расчетциклаупр2.py"""
    r = 0.75
    p = (pritok_proj / podacha) * t_cycle
    u = power_kw * ((p - r) * t_razgon_sec / 60) / t_cycle
    return {
        "Время работы (мин)":                                p,
        "Время накопления (мин)":                            t_cycle - p,
        "Средняя мощность при периодической работе (кВт)":   u,
    }


# ──────────────────────── ГАЗ / СЕПАРАЦИЯ ────────────────────────

def soderzh_gaza(k_nkt, Q_zhid_surf, S_priem, V_pyz_sms, P_priem_atm,
                 P_nasys_atm, gaz_faktor):
    """Источник: содержгазанавходевнасос.py"""
    t = Q_zhid_surf * k_nkt
    y = 1 / (1 + (6.02 * t / S_priem))
    u = gaz_faktor * (1 - (P_priem_atm / P_nasys_atm))
    a = t / S_priem
    s = (1 / a * (((1 + P_priem_atm) * k_nkt) / u)) + 1
    d = t * s / (1 - s)
    f = d / S_priem
    h = s * (1 - y)
    g = s / (1 + (V_pyz_sms / f) * h)
    return {"Истинное содержание свободного газа на входе (доли)": g}


def uchet_gaza(k_nat_sep, k_gas_sep, V_gas_total, Q_gas_meas, Q_oil_meas):
    """Источник: учетвлияниягаза.py"""
    return {
        "Газовый фактор по замерам (м³/м³)":           Q_gas_meas / Q_oil_meas,
        "Доля свободного газа, поступающая в насос":   1 - ((1 - k_nat_sep) * (1 - k_gas_sep)),
    }


# ───────────── ГЕОМЕТРИЯ / ПРОМЫВКА ─────────────

def ploshchad_kolts(D_ek_mm, D_ped_mm):
    """Источник: площадь_кольц_простр.py (формула сохранена как в исходнике)"""
    return {"Площадь кольцевого пр-ва (м²)":
            3.14 * ((D_ek_mm / 2000) ** 2) - ((D_ped_mm / 2000)) ** 2}


def izgib_uec(D_ek_mm, D_max_uec_mm, L_uec_m):
    """Источник: нулевойизгибуэцнвинтспуска.py"""
    r = ((D_ek_mm - D_max_uec_mm) / 2) / 1000
    h = (40 * r) / (4 * (r ** 2) + (L_uec_m ** 2))
    n_rad = h * math.pi / 180
    try:
        asn = math.asin(n_rad)
    except ValueError:
        asn = float("nan")
    return {"Нулевой изгиб установки (°/10 м)": asn}


def promyvka_obem(D_ek_mm, D_nkt_mm, H_stat):
    """Источник: минимальныйvпромывкиУЭЦН.py"""
    t = (3.14 * (D_ek_mm ** 2 / 1000)) / 4
    y = (3.14 * (D_nkt_mm ** 2 / 1000)) / 4
    return {"Минимальный объём промывки УЭЦН (м³)": ((t - y) * H_stat) / 1000}
