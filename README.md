#Introducción

El proyecto consiste en realizar dos implementaciones para comunicar datos entre clientes Android y un servidor centralizado. Estos sistemas de comunicación son una parte de mensajería muy común en aplicaciones para móviles, por ejemplo juegos o aplicaciones que usan geolocalización. En estos sistemas es muy importante su característica de tiempo real es decir que sirva para sistemas interactivos.

Aunque no es un problema novedoso, interesa probar implementaciones para comparar diferencias en las prestaciones, para proporcionar ejemplos didácticos y, hasta cierto punto, que se pueden dejar como bibliotecas reutilizables de código abierto.

En este breve documento se presentan dos trabajos académicamente dirigidos para sustituir la estancia en práctica y proyecto que se desarrollaba en la empresa Soluciones Cuatroochenta SA y que ha sido interrumpido por la situación de emergencia.

#Propuesta con API Rest

En esta propuesta el desarrollo se basa en el modelo API Rest. Las comunicaciones se harán con el protocolo http (sobre TCP). El objetivo es enviar y recibir datos entre terminales Android y un servidor. La aplicación de los terminales Android se implementará con el entorno Kivy y la parte del servidor con la plataforma Flask.

En la parte del servidor, la información recibida se guardará en una base de datos relacional utilizando SQLAlchemy para poder hacer un tratamiento de los datos y enviar respuesta a los clientes Android.

Se realizará un pequeño ejemplo de aplicación de todo el sistema.

El servidor desarrollado con Flask puede servir para el sistema desarrollado con UDP si en el otro proyecto se realiza una pasarela entre los mensajes UDP y el modelo API Rest, que deberían ejecutarse en el mismo servidor para no afectar a las prestaciones.

Todo este proyecto se desarrollaría en Python.



## Instalación del entorno virtual 


Creación entorno virtual Windows (Python 3.5+)
```
Si tienes el python en las variables de entorno:

c:\> python -m venv \path\to\myenv

Si no lo tienes:

c:\Python35\> python -m venv \path\to\myenv
```

Creación del entorno vitual Linux
```
virtualenv -p python3 python3env
source python3env/bin/activate
```

## Instalación de las dependencias 

###Instalación automática 
```
pip install -r requirements.txt
```

### Instalación manual
Instalación de las dependencias de flask
```
pip install flask
pip install flask-login
pip install flask-babel
pip install flask_sqlalchemy
# Cualquier otra dependencia
```

Instalación de las dependencias de kivy

```
pip install kivy
pip install buildozer 
# Cualquier otra dependencia
```

