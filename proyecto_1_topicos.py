from pyfiglet import Figlet
from tabulate import tabulate
import numpy as np
import requests


def main():
    figlet = Figlet()
    output_title = figlet.setFont(font = 'big')
    output_title = figlet.renderText('Levelised Cost of Hydrogen')
    print(f'{output_title}\n')
    print("PROYECTO 1 - TÓPICOS\n")
    print("Authors: Juan Sebastián Caicedo, Juliana Delgadillo & Riccardo Toscani")
    values = get_initial_data()
    lcoe = LCOE(*values)
    VPN = lcoe.VPN()
    print("\nOUTPUS\n")
    print(lcoe.LCOH(VPN))

def get_initial_data():
    while True:
        try:
            installed_power = input("Ingrese el valor de la potencia instalada (MW): ")
            installed_power = float(installed_power.strip())
            break
        except ValueError:
            print("La potencia instalada es inválida, inténtelo nuevamente")
    while True:
        try:
            energia_generada_anual = input("Ingrese la energía generada anual (MWh): ")
            energia_generada_anual = float(energia_generada_anual.strip())
            break
        except ValueError:
            print("La energía generada anual es inválida, inténtelo nuevamente")
    while True:
        try:
            CAPEX = input("Ingrese el CAPEX del proyecto ($/MW): ")
            CAPEX = float(CAPEX.strip())
            break
        except ValueError:
            print("El CAPEX es inválido, inténtelo nuevamente")
    while True:
        try:
            OPEX = input("Ingrese el OPEX como porcentaje del CAPEX (%): ")
            OPEX = OPEX.strip()
            if '/' in OPEX:
                OPEX = fraction_to_float(OPEX)
            OPEX = float(OPEX)
            break
        except ValueError:
            print("El OPEX es inválido, inténtelo nuevamente")
    while True:
        try:
            tiempo_de_construccion = input("Ingrese el tiempo de construcción de la planta (años): ")
            tiempo_de_construccion = float(tiempo_de_construccion.strip())
            break
        except ValueError:
            print("La energía generada anual es inválida, inténtelo nuevamente")
    while True:
        try:
            vida_util = input("Ingrese la vida útil del proyecto (años): ")
            vida_util = float(vida_util.strip())
            break
        except ValueError:
            print("La vida útil es inválida, inténtelo nuevamente")
    while True:
        try:
            tasa_interes = input("Ingrese la tasa de interés (%): ")
            tasa_interes = tasa_interes.strip()
            if '/' in tasa_interes:
                tasa_interes = fraction_to_float(tasa_interes)
            tasa_interes = float(tasa_interes)
            break
        except ValueError:
            print("La tasa de interés es inválida, inténtelo nuevamente")
    while True:
        try:
            inflacion = input("Ingrese la inflación (%): ")
            inflacion = inflacion.strip()
            if '/' in inflacion:
                inflacion = fraction_to_float(inflacion)
            inflacion = float(inflacion)
            break
        except ValueError:
            print("La tasa de interés es inválida, inténtelo nuevamente")
    while True:
        try:
            factor_degradacion = input("Ingrese el factor de degeneración (%): ")
            factor_degradacion = factor_degradacion.strip()
            if '/' in factor_degradacion:
                factor_degradacion = fraction_to_float(factor_degradacion)
            factor_degradacion = float(factor_degradacion)
            break
        except ValueError:
            print("El factor de degradación es inválido, inténtelo nuevamente")
    while True:
        try:
            factor_planta = input("Ingrese el factor de planta (%): ")
            factor_planta = factor_planta.strip()
            if '/' in factor_planta:
                factor_planta = fraction_to_float(factor_planta)
            factor_planta = float(factor_planta)
            break
        except ValueError:
            print("El factor de planta es inválido, inténtelo nuevamente")
    return [installed_power, energia_generada_anual, CAPEX, OPEX,tiempo_de_construccion, vida_util, tasa_interes, inflacion, factor_degradacion, factor_planta]

        

def fraction_to_float(fraction_str):
    if '/' in fraction_str:
        numerator, denominator = map(int, fraction_str.split('/'))
        return float(numerator/denominator)
    else:
        return float(fraction_str)
    
class LCOE:
    def __init__(self, installed_power, energia_generada_anual, CAPEX, OPEX,tiempo_de_construccion, vida_util, tasa_interes, inflacion, factor_degradacion, factor_planta):
        self.installed_power = installed_power
        self.energia_generada_anual = energia_generada_anual
        self.CAPEX = CAPEX
        self.OPEX = OPEX/100
        self.tiempo_de_construccion = tiempo_de_construccion
        self.vida_util = vida_util
        self.tasa_interes = tasa_interes/100
        self.inflacion = inflacion/100
        self.factor_degradacion = factor_degradacion/100
        self.factor_planta = factor_planta/100

    def VPN(self):
        VP_cost = []
        tasa_intereses = [1]
        opex = [0, 0, self.CAPEX*self.OPEX]
        for i in range(1, int(self.vida_util)+1):
            tasa_de_i = tasa_intereses[i-1]/(1+self.tasa_interes)
            tasa_intereses.append(tasa_de_i)
            current_capex = self.CAPEX/(1+tasa_de_i)**i
            if i > self.tiempo_de_construccion:
                opex.append(opex[i-1]*(1+self.inflacion))
            costo_total = current_capex+opex[i-1]
            VP_cost += [costo_total*tasa_de_i]
        return sum(VP_cost)/(8760*self.factor_planta)
        

    def get_TRM(self):
        url = "https://www.datos.gov.co/resource/32sa-8pi3.json"
        response = requests.get(url)
        data = response.json()
        return float(data[0]['valor'])
    
    def LCOH(self, VPN):
        TRM = self.get_TRM()
        table = np.array([
            ["Moneda", "LCOE ($/MW)", "LCOE ($/KW)"], 
            ["COP", "${:,.2f}".format(VPN), "${:,.2f}".format(VPN/1000)], 
            ["USD", "${:,.2f}".format(VPN/TRM), "${:,.2f}".format(VPN/(TRM*1000))], 
            
        ])
        return tabulate(table[1:], headers=table[0], tablefmt="grid")

if __name__ == '__main__':
    main()