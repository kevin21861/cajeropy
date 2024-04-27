import mysql.connector
import re
class CajeroAutomatico:
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bancolombia"
        )

    def __del__(self):
        self.conexion.close()



    def validar_numero(self):
        numero = input('Ingrese su número telefónico: ')
        if len(numero) == 10 or len(numero) == 11:
            print("Número válido")
            return True
            
        
 
    def validador(self, msj):
        while True:
            msj_input = input(msj)
            if msj_input.isdigit():
                return int(msj_input)
            elif msj_input.replace('.', '', 1).isdigit():
                return float(msj_input)
            else:
                print("Invalido")
            
        
    def imprimir_menu(self):
        print("\nSeleccione el monto:")
        print("1. 20.000")
        print("2. 50.000")
        print("3. 100.000")
        print("4. 200.000")
        print("5. 500.000")
        print("6. 300.000")
        print("7. 1.000.000")
        print("8. Otro valor")

    def generar_montos_disponibles(self):
        return {
            1: 20000,
            2: 50000,
            3: 100000,
            4: 200000,
            5: 500000,
            6: 300000,
            7: 1000000
        }

    def validar_cliente(self, cedula, clave):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cedula = %s AND clave = %s", (cedula, clave))
        cliente = cursor.fetchone()
        cursor.close()
        return cliente

    def validar_clave(self, clave):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM clientes WHERE clave = %s LIMIT 1", (clave,))
        cliente = cursor.fetchone()
        cursor.close()
        return cliente

    def consultar_saldo(self, cliente_id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT saldo FROM clientes WHERE id = %s", (cliente_id,))
        saldo = cursor.fetchone()[0]
        cursor.close()
        return saldo
    
    def actualizar_saldo(self, cliente_id, nuevo_saldo):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE clientes SET saldo = %s WHERE id = %s", (nuevo_saldo, cliente_id))
        self.conexion.commit()
        cursor.close()

    def actualizar_saldo_tarjeta(self, cliente_id, nuevo_saldo):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE clientes SET saldo_tarjeta = %s WHERE id = %s", (nuevo_saldo, cliente_id))
        self.conexion.commit()
        cursor.close()

    def consultar_saldo_tarjeta(self, cliente_id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT saldo_tarjeta FROM clientes WHERE id = %s", (cliente_id,))
        saldo = cursor.fetchone()[0]
        cursor.close()
        return saldo
    
    def avances(self, valor, cliente_id):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE clientes SET saldo_tarjeta = saldo_tarjeta - %s WHERE id = %s", (valor, cliente_id))
        cursor.execute("UPDATE clientes SET saldo = saldo + %s WHERE id = %s", (valor, cliente_id))
        self.conexion.commit()
        cursor.close()

    def transfer(self, valor, cliente_id):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE clientes SET saldo_tarjeta = saldo_tarjeta - %s WHERE id = %s", (valor, cliente_id))
        cursor.execute("UPDATE clientes SET saldo = saldo + %s WHERE id = %s", (valor, cliente_id))
        self.conexion.commit()
        cursor.close()

    def retiro_ahorros_corriente(self, cliente_id):
        saldo_actual = self.consultar_saldo_tarjeta(cliente_id)
        print("Su saldo actual tarjeta es:", saldo_actual)
        self.imprimir_menu()
        opcion_monto = self.validador('Seleccione el monto a retirar: ')
        montos_disponibles = self.generar_montos_disponibles()

        if opcion_monto in montos_disponibles:
            monto = montos_disponibles[opcion_monto]
            clave = input("Ingrese la clave con la cual inicio sesión: ")
            cliente = self.validar_clave(clave)

            if cliente:
                if saldo_actual >= monto:
                    nuevo_saldo = saldo_actual - monto
                    self.actualizar_saldo_tarjeta(cliente_id, nuevo_saldo)
                    print('Retiro exitoso. Nuevo saldo:', nuevo_saldo)
                else:
                    print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
            else:
                print('Clave incorrecta')
        elif opcion_monto == 8:
            monto_personalizado = self.validador('Ingrese el monto a retirar: ')

            if monto_personalizado % 10000 == 0 and monto_personalizado > 0:
                clave = input("Ingrese la clave con la cual inicio sesión: ")
                cliente = self.validar_clave(clave)  # Corregido aquí
                if cliente: 
                    if saldo_actual >= monto_personalizado:
                        nuevo_saldo = saldo_actual - monto_personalizado
                        self.actualizar_saldo_tarjeta(cliente_id, nuevo_saldo)
                        print('Retiro exitoso. Nuevo saldo:', nuevo_saldo)
                    else:
                        print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
                else:
                    print('Clave incorrecta')
            else:
                print("El monto debe ser múltiplo de 10.000 y mayor que cero.")
        else:
            print("Opción inválida")

    def servicios(self, cliente_id):

        codigo_convenio = self.validador('Ingresa el código de convenio de su factura de 8 dígitos: ')
       
        if len(str(codigo_convenio)) == 8:
            print('Elige el método de pago')
            print('1. Saldo (efectivo)')
            print('2. Tarjeta')

            opciones = {
                1: 'saldo',
                2: 'tarjeta'     
            }
            opcion_elegida = self.validador('ingresa: ')
            if opcion_elegida in opciones:
                if opciones[opcion_elegida] == 'saldo':
                    saldo_actual = self.consultar_saldo(cliente_id)
                    monto = self.validador('Ingrese el monto a pagar de su servicio: ')
                    clave = input("Ingrese la clave con la cual inició sesión: ")
                    cliente = self.validar_clave(clave)
                    if cliente:
                        if saldo_actual >= monto:
                            nuevo_saldo = saldo_actual - monto
                            self.actualizar_saldo(cliente_id, nuevo_saldo)
                            print('Número de convenio: ', codigo_convenio)
                            print('El servicio ha sido pagado con éxito, su saldo es de: ', nuevo_saldo)
                        else:
                            print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
                    else:
                        print('Clave incorrecta')
                elif opciones[opcion_elegida] == 'tarjeta':
                    saldo_actual = self.consultar_saldo_tarjeta(cliente_id)
                    monto = self.validador('Ingrese el monto a pagar de su servicio: ')
                    clave = input("Ingrese la clave con la cual inició sesión: ")
                    cliente = self.validar_clave(clave)
                    if cliente:
                        if saldo_actual >= monto:
                            nuevo_saldo = saldo_actual - monto
                            self.actualizar_saldo_tarjeta(cliente_id, nuevo_saldo)
                            print('Número de convenio: ', codigo_convenio)
                            print('El servicio ha sido pagado con éxito, su saldo es de: ', nuevo_saldo)
                        else:
                            print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
                    else:
                        print('Clave incorrecta')
            else:
                print('Opción inválida')
        else:
            print('Código inválido')   
            

    def transferencia(self, cliente_id):
        
        codigo_convenio = self.validador('Ingresa el código de convenio de su factura de 8 dígitos: ')
        if len(str(codigo_convenio)) == 8:
            print('Elige el método de pago')
            print('1. Saldo (efectivo)')
            print('2. Tarjeta')

            opciones = {
                1: 'saldo',
                2: 'tarjeta'     
            }
            opcion_elegida = self.validador('ingresa : ')
            if opcion_elegida in opciones:
                if opciones[opcion_elegida] == 'saldo':
                    saldo_actual = self.consultar_saldo(cliente_id)
                    monto = self.validador('Ingrese el monto a pagar de su servicio: ')
                    clave = input("Ingrese la clave con la cual inició sesión: ")
                    cliente = self.validar_clave(clave)
                    if cliente:
                        if saldo_actual >= monto:
                            nuevo_saldo = saldo_actual - monto
                            self.actualizar_saldo(cliente_id, nuevo_saldo)
                            print('Número de convenio: ', codigo_convenio)
                            print('El servicio ha sido pagado con éxito, su saldo es de: ', nuevo_saldo)
                        else:
                            print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
                    else:
                        print('Clave incorrecta')
                elif opciones[opcion_elegida] == 'tarjeta':
                    saldo_actual = self.consultar_saldo_tarjeta(cliente_id)
                    monto = self.validador('Ingrese el monto a pagar de su servicio: ')
                    clave = input("Ingrese la clave con la cual inició sesión: ")
                    cliente = self.validar_clave(clave)
                    if cliente:
                        if saldo_actual >= monto:
                            nuevo_saldo = saldo_actual - monto
                            self.actualizar_saldo_tarjeta(cliente_id, nuevo_saldo)
                            print('Número de convenio: ', codigo_convenio)
                            print('El servicio ha sido pagado con éxito, su saldo es de: ', nuevo_saldo)
                        else:
                            print("Saldo insuficiente. Su saldo actual es:", saldo_actual)
                    else:
                        print('Clave incorrecta')
            else:
                print('Opción inválida')
        else:
            print('Código inválido')  







    def bancolombia_nequi(self, cliente_id):
       # if self.msj("nequi"):
            
            if self.validar_numero()  :
                
                
                print("Número válido")
                self.imprimir_menu()
                opcion_monto = self.validador('Seleccione el monto a retirar: ')
                montos_disponibles = self.generar_montos_disponibles()

                if opcion_monto in montos_disponibles:
                    monto = montos_disponibles[opcion_monto]
                    print('\n==================================================' )
                    print('\nIngrese el codigo de 6 digitos: ')
                    print('\n==================================================' )
                    retirar_codigo = self.validador('Ingrese el código: ')
                    if len(retirar_codigo) == 6:
                        saldo_actual = self.consultar_saldo(cliente_id)
                        if saldo_actual >= monto:
                            nuevo_saldo = saldo_actual - monto
                            self.actualizar_saldo(cliente_id, nuevo_saldo)
                            print('Retiro exitoso. Nuevo saldo:', nuevo_saldo)
                        else:
                            print("Saldo insuficiente")
                    else:
                        print('Código inválido')
                elif opcion_monto == 8:
                    monto_personalizado = self.validador('Ingrese el monto a retirar: ')
                    if monto_personalizado % 10000 == 0 and monto_personalizado > 0:
                        print('\n==================================================' )
                        print('\nIngrese el codigo de 6 digitos: ')
                        print('\n==================================================' )
                        retirar_codigo = self.validador('Ingrese el código: ')
                        if len(retirar_codigo) == 6:
                            saldo_actual = self.consultar_saldo(cliente_id)
                            if saldo_actual >= monto_personalizado:
                                nuevo_saldo = saldo_actual - monto_personalizado
                                self.actualizar_saldo(cliente_id, nuevo_saldo)
                                print('Retiro exitoso. Nuevo saldo:', nuevo_saldo)
                            else:
                                print("Saldo insuficiente")
                        else:
                            print('Código inválido')
                    else:
                        print("El monto debe ser múltiplo de 10.000 y mayor que cero.")
                else:
                    print("Opción inválida")
            else:
                print('Número inválido')

    def retirar_efectivo(self, cliente_id):
        print("\nSeleccione el tipo de cuenta:")
        print("1. Cuenta de ahorros")
        print("2. Cuenta corriente")
        print("3. Nequi")
        print("4. Bancolombia a la mano")
        tipo_cuenta = self.validador("Seleccione el tipo de cuenta: ")
        if tipo_cuenta == 1:
            self.retiro_ahorros_corriente(cliente_id)
        elif tipo_cuenta == 2:
            self.retiro_ahorros_corriente(cliente_id)
        elif tipo_cuenta == 3:
            self.bancolombia_nequi(cliente_id)
        elif tipo_cuenta == 4:
            
            self.bancolombia_nequi(cliente_id)
            
                
        else:
            print("Opción inválida")

            

    def realizar_avance_efectivo(self, cliente_id):
     valor =  self.validador("Ingrese el valor de su avance: ")
     saldo_actual = self.consultar_saldo_tarjeta(cliente_id)
     if saldo_actual >= valor:
        # if valor % 10000 == 0 and valor > 0:
            print("Realizando avance en efectivo...")
            self.avances(valor, cliente_id)
            # print("Su saldo en su cuenta es:", cajero.consultar_saldo(cliente_id))
            print("Su saldo actual de su tarjeta es:", cajero.consultar_saldo_tarjeta(cliente_id))
        # else:
        #     print('debe de ser multiplos de 10.000 o mayor a 0')
     else:
        print('error')
#  if len(retirar_codigo) == 6:
#                         saldo_actual = self.consultar_saldo(cliente_id)
#                         if saldo_actual >= monto:
#                             nuevo_saldo = saldo_actual - monto
#                             self.actualizar_saldo(cliente_id, nuevo_saldo)
#                             print('Retiro exitoso. Nuevo saldo:', nuevo_saldo)
#                         else:
#                             print("Saldo insuficiente")

    

    def avances2(self, valor, cliente_id):
        cursor = self.conexion.cursor()

    # Resta el valor del saldo_tarjeta del cliente
        cursor.execute("UPDATE clientes SET saldo = saldo - %s WHERE id = %s", (valor, cliente_id))
    # Suma el valor a la columna saldo en la tabla otro_cliente
        cursor.execute("UPDATE otro_cliente SET saldo = saldo + %s WHERE id = %s", (valor, cliente_id))
        #cursor.execute("UPDATE otro_cliente SET saldo = saldo + %s WHERE cuenta = (SELECT cuenta FROM clientes WHERE id = %s)", (valor, cliente_id))
        self.conexion.commit()
        cursor.close()


    def realizar_transferencia(self, cliente_id):
        print("Realizando transferencia...")
        # Aquí puedes implementar la lógica para realizar transferencias
        print("\nSeleccione el tipo de cuenta:")
        print("1. Cuenta Bancolombia")
        print("2. Cuenta inscrita")
        print("3. Cuenta no inscrtia")
        tipo_cuenta = self.validador("Seleccione el tipo de cuenta: ")
        valor = self.validador("Ingrese el valor : ")
        # Aquí puedes implementar la lógica para cada tipo de cuenta
        if tipo_cuenta == 1:
                if valor % 10000 == 0 and valor > 0:
                    print("\nRealizando transferencia en efectivo...")
                    print
                    self.avances2(valor, cliente_id)
                    cliente = cajero.validar_cliente(cedula, clave)
                    cliente_id = cliente[0] 
                    print("Bienvenido,", cliente[1], cliente[2])
                    print("Su saldo en su cuenta es:", cajero.consultar_saldo(cliente_id))
                   
                else:
                    print('debe de ser multiplos de 10.000 o mayor a 0')
               
        elif tipo_cuenta == 2:
            pass
        elif tipo_cuenta == 3:
             pass
        else:
            print("Opción inválida")
            

    def pagar_servicio(self, cliente_id):
        print("Pagando servicio...")
        # Aquí puedes implementar la lógica para pagar servicios
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id, nombre FROM servicios")
        servicios = cursor.fetchall()
        print("\nSeleccione el tipo de servicio:")
        for tipo in servicios:
            print(f"{tipo[0]}. {tipo[1]}")
        tipo_cuenta = self.validador("Seleccione el tipo de cuenta: ")
        
        # Aquí puedes implementar la lógica para cada tipo de cuenta
        if tipo_cuenta == 1:
            self.servicios(cliente_id)
            pass
        elif tipo_cuenta == 2:
            pass
        elif tipo_cuenta == 3:
            pass
        elif tipo_cuenta == 4:
            pass
        elif tipo_cuenta == 5:
           pass
        elif tipo_cuenta == 6:
           pass
        elif tipo_cuenta == 7:
           pass
        elif tipo_cuenta == 8:
           pass
        elif tipo_cuenta == 9:
           pass
        elif tipo_cuenta == 10:
           pass
        elif tipo_cuenta == 11:
           pass
        elif tipo_cuenta == 12:
            pass
        else:
            print("Opción inválida")

    def cambiar_clave(self, cliente_id):
        nueva_clave = input("Ingrese la nueva clave: ")
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE clientes SET clave = %s WHERE id = %s", (nueva_clave, cliente_id))
        self.conexion.commit()
        cursor.close()
        print("Clave cambiada exitosamente")

# Ejemplo de uso del cajero automático
cajero = CajeroAutomatico()


# Solicitar información de cliente
cedula = input("Ingrese su número de cédula: ")
clave = input("Ingrese su clave: ")

cliente = cajero.validar_cliente(cedula, clave)

if cliente:
    cliente_id = cliente[0]  # Suponiendo que el ID del cliente es el primer campo en la tabla
    print('\n==================================================\n' )
    print("Bienvenido,", cliente[2], cliente[3])

    while True:
        print('\n==================================================' )
        print("\nSeleccione una opción:")
        print('+++++++++++++++++++++++++++++++++' )
        print("1. Consultar saldo")
        print('+++++++++++++++++++++++++++++++++' )
        print("2. Retirar efectivo")
        print('+++++++++++++++++++++++++++++++++' )
        print("3. Realizar avance en efectivo")
        print('+++++++++++++++++++++++++++++++++' )
        print("4. Realizar transferencia")
        print('+++++++++++++++++++++++++++++++++' )
        print("5. Pagar servicio")
        print('+++++++++++++++++++++++++++++++++' )
        print("6. Cambiar clave principal")
        print('+++++++++++++++++++++++++++++++++' )
        print("7. Salir")
        print('\n==================================================' )
        #validador = validador()
        opcion = int(input("Elige la opción: ") ) 
        

        if opcion == 1:
            print("Su saldo en su cuenta es:", cajero.consultar_saldo(cliente_id))
            print("Su saldo actual de su tarjeta es:", cajero.consultar_saldo_tarjeta(cliente_id))
        elif opcion == 2:
                cajero.retirar_efectivo(cliente_id)
        elif opcion == 3:
                cajero.realizar_avance_efectivo(cliente_id)
        elif opcion == 4:
                cajero.realizar_transferencia(cliente_id)
        elif opcion == 5:
                cajero.pagar_servicio(cliente_id)
        elif opcion == 6:
                cajero.cambiar_clave(cliente_id)
        elif opcion == 7:
                print("Gracias por utilizar Cajero Automático. ¡Hasta luego!")
                break
        else:
            print("Opción inválida")
else:
    print("Número de cédula o clave incorrectos. Por favor, inténtelo de nuevo.")
