import json
import spacy
from limpieza_texto import limpieza_basica
from lenguajes import detectar_lenguaje, definir_lenguaje

### Definir clases para el lematizador ###


class Lematizador_spacy():
    def __init__(self, lenguaje, dict_lemmas=None, dim_modelo='md'):
        # Definir lenguaje del lematizador
        self.definir_lenguaje(lenguaje)
        # Inicializar lematizador
        self.iniciar_lematizador(dim_modelo)
        # Si se introdujo un diccionario personalizado, se utiliza
        if isinstance(dict_lemmas, dict):
            self.modificar_lemmas(dict_lemmas)
        # Si es la ubicación del archivo, primero se carga
        elif isinstance(dict_lemmas, str):
            try:
                dict_lemmas = json.load(open(dict_lemmas))
                self.modificar_lemmas(dict_lemmas)
            except BaseException:
                print('No se pudo cargar el diccionario de lemas')

    def definir_lenguaje(self, lenguaje):
        self.leng = definir_lenguaje(lenguaje)

    def iniciar_lematizador(self, dim_modelo):
        self.lematizador = None
        if self.leng is not None:
            from utils.spacy_funcs import cargar_modelo
            self.lematizador = cargar_modelo(dim_modelo, self.leng)

    def modificar_lemmas(self, dict_lemmas):
        # Definir función auxiliar
        def cambiar_propiedades_lemma(doc):
            for token in doc:
                if(token.text in dict_lemmas):
                    token.lemma_ = dict_lemmas[token.text]
            return doc
        # Aplicar la función para modificar el lematizador
        if (self.lematizador is not None) and (self.lematizador != -1):
            self.lematizador.add_pipe(cambiar_propiedades_lemma, first=True)

    def lematizar(self, texto, limpiar=True):
        if limpiar:
            texto = limpieza_basica(texto)
        return ' '.join([token.lemma_ for token in self.lematizador(texto)])

# Implementación alternativa, utilizando stanza


class Lematizador_stanza():
    def __init__(
            self,
            lenguaje,
            lemma_model_path='',
            dict_lemmas=None,
            out_path=''):
        # Definir lenguaje del lematizador
        self.definir_lenguaje(lenguaje)
        # Inicializar lematizador
        self.iniciar_lematizador(lemma_model_path)
        # Si se introdujo un diccionario personalizado, se utiliza
        if isinstance(dict_lemmas, dict):
            self.modificar_lemmas(dict_lemmas, lemma_model_path, out_path)
        # Si es la ubicación del archivo, primero se carga
        elif isinstance(dict_lemmas, str):
            try:
                dict_lemmas = json.load(open(dict_lemmas))
                self.modificar_lemmas(dict_lemmas)
            except BaseException:
                print('Debe proporcionar la ubicación de un archivo válido')

    def definir_lenguaje(self, lenguaje):
        self.leng = definir_lenguaje(lenguaje)

    def iniciar_lematizador(self, lemma_model_path):
        from utils.stanza_funcs import stanza_pipeline
        self.lematizador = None
        if self.leng is not None:
            self.lematizador = stanza_pipeline(
                self.leng, lemma_model_path=lemma_model_path)

    def modificar_lemmas(
            self,
            dict_lemmas,
            in_path='',
            out_path='',
            location='cpu'):
        from utils.stanza_funcs import modificar_modelo
        self.lematizador = modificar_modelo(
            self.lematizador,
            'lemma',
            dict_lemmas,
            in_path,
            out_path,
            location)

    def lematizar(self, texto, limpiar=True):
        if limpiar:
            texto = limpieza_basica(texto)
        doc = self.lematizador(texto)
        # Extraer los lemas de cada palabra, de cada frase, y juntarlos
        return ' '.join([w.lemma for s in doc.sentences for w in s.words])
        # return ' '.join([i['lemma'] for i in doc.to_dict()[0]])


### Definir función que envuelva la funcionalidad básica de las clases ###

def lematizar_texto(
        texto,
        lenguaje='es',
        libreria='spacy',
        limpiar=True,
        lematizador=None,
        dict_lemmas=None,
        dim_modelo='md',
        lemma_model_path='',
        out_path=''):
    # Si no se provee un lematizador, este debe ser inicializado
    if lematizador is None:
        if lenguaje == 'auto':
            lenguaje = detectar_lenguaje(texto)
        if libreria.lower() == 'spacy':
            lematizador = Lematizador_spacy(lenguaje, dict_lemmas, dim_modelo)
        elif libreria.lower() == 'stanza':
            lematizador = Lematizador_stanza(
                lenguaje, lemma_model_path, dict_lemmas, out_path)
        else:
            print(
                'Por favor escoja una librería válida para el lematizador (Spacy o Stanza)')
            return None
    # Si el lenguaje no se reconoce, se envía mensaje
    if lematizador.lematizador is None:
        print('Lenguaje no válido.')
        return None
    # Devolver la lematización del texto
    return lematizador.lematizar(texto, limpiar)
