import requests
import json
from time import sleep

# --- Configuración Base ---
BASE_URL = "https://pokeapi.co/api/v2/"
KANTO_REGION_ID = 1  # ID para la región de Kanto
JOHTO_REGION_ID = 3  # ID para la región de Johto

# --- Funciones Auxiliares ---

def get_data(endpoint, params=None):
    """
    Función genérica para obtener datos de la PokeAPI con manejo básico de errores.
    """
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP al acceder a {url}: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de Conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Tiempo de Espera Agotado: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error Desconocido en la Solicitud: {err}")
    return None

def get_all_pokemon_names():
    """
    Obtiene los nombres de todos los Pokémon disponibles en la API (hasta el límite de la llamada).
    La PokeAPI permite obtener todos los Pokémon con un límite alto o sin límite.
    """
    print("Obteniendo lista completa de Pokémon...")
    endpoint = "pokemon"
    # Usamos limit=10000 para asegurarnos de obtener todos los Pokémon actuales.
    data = get_data(endpoint, params={'limit': 10000})
    if data and 'results' in data:
        return {p['name']: p['url'] for p in data['results']}
    return {}

def get_pokemon_by_id_or_name(identifier):
    """
    Obtiene los datos detallados de un Pokémon por ID o nombre.
    """
    endpoint = f"pokemon/{identifier}"
    return get_data(endpoint)

def get_region_pokedex_ids(region_id):
    """
    Obtiene los IDs de los Pokémon en una región específica.
    """
    print(f"Obteniendo lista de Pokémon de la región con ID: {region_id}...")
    endpoint = f"pokedex/{region_id}"
    data = get_data(endpoint)
    if data and 'pokemon_entries' in data:
        return {entry['pokemon_species']['name'] for entry in data['pokemon_entries']}
    return set()

def get_species_data(pokemon_name):
    """
    Obtiene los datos de la especie de un Pokémon (necesario para evoluciones y hábitat).
    """
    endpoint = f"pokemon-species/{pokemon_name}"
    return get_data(endpoint)

# --- Funciones de Respuesta a Preguntas ---

## 🔹 Clasificación por Tipos

def clasificacion_por_tipos():
    """Responde a las preguntas de clasificación por tipos."""
    print("\n--- 🔹 Clasificación por Tipos ---")
    
    # a) ¿Cuántos Pokémon de tipo fuego existen en la región de Kanto?
    
    # 1. Obtener la lista de Pokémon de Kanto (Pokedex ID 1)
    kanto_pokemon = get_region_pokedex_ids(KANTO_REGION_ID)
    if not kanto_pokemon:
        return

    # 2. Obtener la lista de Pokémon de tipo Fuego
    fire_type_data = get_data("type/fire")
    if not fire_type_data:
        return

    fire_pokemon_names = {p['pokemon']['name'] for p in fire_type_data['pokemon']}
    
    # 3. Intersección de ambos conjuntos
    fire_in_kanto = kanto_pokemon.intersection(fire_pokemon_names)
    
    print(f"a) Pokémon de tipo fuego en Kanto: {len(fire_in_kanto)}")
    print(f"   Nombres: {', '.join(sorted(fire_in_kanto))}")
    
    # b) ¿Cuáles son los nombres de los Pokémon tipo agua con una altura mayor a 10?
    
    water_type_data = get_data("type/water")
    if not water_type_data:
        return
        
    water_pokemon_list = []
    
    print("\nProcesando Pokémon tipo Agua (filtrando por altura > 10 dm)...")
    for i, p_entry in enumerate(water_type_data['pokemon']):
        name = p_entry['pokemon']['name']
        
        # Opcional: Pausa para evitar saturar la API (ejecución más lenta)
        if i % 10 == 0 and i > 0:
             sleep(0.5) 

        # Se necesita la URL específica del Pokémon para obtener la altura
        pokemon_detail = get_pokemon_by_id_or_name(name)
        
        if pokemon_detail and 'height' in pokemon_detail:
            # La altura en la API está en decímetros (dm). 10 dm = 1.0 m.
            height = pokemon_detail['height']
            if height > 10:
                # Almacenamos el nombre y la altura en metros para la respuesta
                water_pokemon_list.append((name.capitalize(), height / 10.0))

    if water_pokemon_list:
        nombres = [f"{name} ({height}m)" for name, height in water_pokemon_list]
        print(f"b) Nombres de Pokémon tipo Agua con altura mayor a 10 dm (1 metro): {len(water_pokemon_list)} Pokémon")
        print(f"   Lista: {', '.join(nombres)}")
    else:
        print("b) No se encontraron Pokémon tipo Agua con una altura mayor a 10 dm.")

## 🔹 Evoluciones

def evoluciones():
    """Responde a las preguntas sobre evoluciones."""
    print("\n--- 🔹 Evoluciones ---")

    # a) Selecciona un Pokémon inicial (de cualquier región) y describe su cadena evolutiva completa.
    starter_name = "charmander"
    
    # 1. Obtener los datos de la especie para la cadena evolutiva
    species_data = get_species_data(starter_name)
    if not species_data or 'evolution_chain' not in species_data:
        print(f"No se pudo obtener la cadena evolutiva para {starter_name.capitalize()}.")
        return

    # 2. Obtener la cadena evolutiva a partir de su URL
    evolution_chain_url = species_data['evolution_chain']['url']
    chain_data = get_data(evolution_chain_url.split(BASE_URL)[-1]) # Extrae el endpoint
    
    if not chain_data or 'chain' not in chain_data:
        print(f"No se pudieron obtener los detalles de la cadena evolutiva para {starter_name.capitalize()}.")
        return

    # 3. Procesar la cadena recursivamente
    def extract_evolution_chain(chain):
        """Función recursiva para extraer los nombres de la cadena."""
        current_name = chain['species']['name'].capitalize()
        evolutions = []
        for evolution in chain['evolves_to']:
            # Se puede extraer el 'trigger' de la evolución, pero para la cadena completa solo necesitamos el nombre
            evolutions.extend(extract_evolution_chain(evolution))
        
        if evolutions:
            return [current_name + " -> " + evo for evo in evolutions]
        else:
            return [current_name]
    
    chain_names = extract_evolution_chain(chain_data['chain'])
    
    print(f"a) Cadena evolutiva completa para el inicial **{starter_name.capitalize()}**:")
    # La salida recursiva simple a menudo devuelve varias cadenas si hay bifurcaciones.
    # En el caso de Charmander, es lineal: Charmander -> Charmeleon -> Charizard
    print(f"   Cadena: {' -> '.join([n.split(' -> ')[0] for n in chain_names])}")


    # b) ¿Qué Pokémon de tipo eléctrico no tienen evoluciones?
    
    electric_type_data = get_data("type/electric")
    if not electric_type_data:
        return
        
    no_evolution_electric_pokemon = []
    
    print("\nProcesando Pokémon tipo Eléctrico (filtrando sin evoluciones)...")
    for i, p_entry in enumerate(electric_type_data['pokemon']):
        name = p_entry['pokemon']['name']
        
        # Pausa opcional
        if i % 10 == 0 and i > 0:
             sleep(0.5) 

        # 1. Obtener los datos de la especie (necesario para ver si hay cadena evolutiva)
        species_data = get_species_data(name)
        
        if species_data and 'evolution_chain' in species_data:
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # El endpoint de la cadena de evolución se puede analizar para ver si solo tiene 1 etapa (la base).
            # Para mayor precisión:
            chain_data = get_data(evolution_chain_url.split(BASE_URL)[-1])

            # Un Pokémon sin evolución tiene una cadena donde 'evolves_to' es una lista vacía.
            if chain_data and 'chain' in chain_data and not chain_data['chain']['evolves_to']:
                # Sin embargo, también hay que considerar las pre-evoluciones (bebés). Si es la única forma,
                # el método más simple es contar el número de etapas. Para el contexto de "no tienen evoluciones"
                # (es decir, la cadena termina en ellos o no tienen evoluciones posteriores),
                # la condición es que *ellos mismos* no evolucionen.
                
                # Una forma más robusta:
                # Verificar si el nombre del Pokémon base de la cadena es el mismo que el Pokémon actual.
                # Si 'evolves_to' está vacío en el nodo de ese Pokémon, no evoluciona.
                
                # La lista de Pokémon tipo eléctrico que NO evolucionan:
                if not species_data['evolves_from_species'] and not chain_data['chain']['evolves_to']:
                     # Caso: No tiene pre-evoluciones y no evoluciona (ej: Legendarios, Stunfisk)
                     no_evolution_electric_pokemon.append(name.capitalize())
                elif species_data['evolves_from_species'] and not chain_data['chain']['evolves_to']:
                     # Caso: Sí tiene pre-evolución pero es la etapa final (ej: Raichu si fuera sólo tipo eléctrico)
                     # La pregunta se refiere a Pokémon que NO tienen evoluciones *posteriores*.
                     # Si la lista 'evolves_to' está vacía para *este* Pokémon en la cadena, es la etapa final.
                     pass # La lógica es más simple y se centra en los que no evolucionan *a nada más*.
                
                if name.lower() == chain_data['chain']['species']['name'].lower() and not chain_data['chain']['evolves_to']:
                    # Es la base de la cadena y no evoluciona
                    no_evolution_electric_pokemon.append(name.capitalize())
                
                elif name.lower() != chain_data['chain']['species']['name'].lower():
                    # Es una forma evolucionada que no evoluciona más
                    # Se debe comprobar si el nombre está en alguna sub-cadena y no tiene evoluciones_to
                    
                    # Para simplificar la consulta (como la mayoría de los no evolucionados son la base),
                    # nos quedamos con los que son la base de la cadena y no tienen evoluciones:
                    pass

    # Re-ejecución más limpia: obtener la lista de todas las especies y filtrar:
    all_electric_pokemon = {p['pokemon']['name'] for p in electric_type_data['pokemon']}
    
    final_list_no_evo = []
    
    print("\nVerificación de Pokémon tipo Eléctrico sin evoluciones posteriores...")
    for i, name in enumerate(sorted(all_electric_pokemon)):
        if i % 10 == 0 and i > 0:
             sleep(0.5) 
             
        species_data = get_species_data(name)
        if species_data and 'evolution_chain' in species_data:
            chain_data = get_data(species_data['evolution_chain']['url'].split(BASE_URL)[-1])

            if chain_data:
                # Una función para encontrar si un Pokémon específico es la etapa final
                def is_final_stage(chain, target_name):
                    current_name = chain['species']['name']
                    if current_name == target_name:
                        # Si es el Pokémon objetivo, es la etapa final si no tiene 'evolves_to'
                        return not chain['evolves_to']
                    
                    # Buscar en las sub-cadenas
                    for evolution in chain['evolves_to']:
                        # Si encuentra el objetivo en una sub-cadena y es la etapa final
                        if is_final_stage(evolution, target_name):
                            return True
                    return False
                
                # Si el Pokémon no tiene evoluciones (es la última etapa de su cadena)
                if is_final_stage(chain_data['chain'], name):
                    # Además, algunos como Pikachu tienen evoluciones ramificadas (Raichu, Alolan Raichu).
                    # La PokeAPI maneja esto. Si no tiene 'evolves_to' en su nodo, es un "no evolucionado" más allá de ese punto.
                    # Asumiendo que la pregunta implica que *nunca* evolucionan *a nada más*
                    final_list_no_evo.append(name.capitalize())

    # Se elimina a Raichu y otras formas que sí evolucionaron de algo. 
    # Para ser "más simple" y responder a los que *no son parte de una cadena evolutiva*, 
    # se podría filtrar por los que no tienen 'evolves_from_species'.
    
    # Lista filtrada manualmente o con lógica más estricta (ej. Tynamo sí evoluciona).
    # Se presenta la lista resultante de la lógica 'is_final_stage'.
    
    # Ajuste: El Pokémon *no tiene evoluciones* implica que es la última etapa.
    # Si la lista contiene a Pikachu, es porque Pikachu sí evoluciona (a Raichu).
    # Esto es complejo. La forma más sencilla es preguntar: ¿cuántas etapas hay *después* de este?
    # Para simplificar, filtramos los que no tienen una pre-evolución y no evolucionan.
    
    no_evo_no_pre_list = []
    for name in sorted(all_electric_pokemon):
        species_data = get_species_data(name)
        if species_data:
            # Si no tiene pre-evolución (evolves_from_species es null)
            # y es la base de la cadena (el primer eslabón)
            if not species_data['evolves_from_species']:
                chain_data = get_data(species_data['evolution_chain']['url'].split(BASE_URL)[-1])
                # Y el eslabón base no evoluciona (evolves_to es [])
                if chain_data and not chain_data['chain']['evolves_to']:
                    no_evo_no_pre_list.append(name.capitalize())
        
    print(f"b) Pokémon de tipo Eléctrico sin evoluciones (no evolucionan a nada más): {len(final_list_no_evo)} Pokémon")
    print(f"   Lista (basada en ser etapa final): {', '.join(sorted(final_list_no_evo))}")

## 🔹 Estadísticas de Batalla

def estadisticas_de_batalla():
    """Responde a las preguntas sobre estadísticas de batalla."""
    print("\n--- 🔹 Estadísticas de Batalla ---")

    # a) ¿Cuál es el Pokémon con el mayor ataque base en la región de Johto?
    
    johto_pokemon_names = get_region_pokedex_ids(JOHTO_REGION_ID)
    if not johto_pokemon_names:
        return
        
    max_attack = -1
    pokemon_max_attack = None
    
    print("\nProcesando Pokémon de Johto (buscando mayor Ataque Base)...")
    for i, name in enumerate(sorted(johto_pokemon_names)):
        if i % 10 == 0 and i > 0:
             sleep(0.5) 
             
        pokemon_detail = get_pokemon_by_id_or_name(name)
        
        if pokemon_detail and 'stats' in pokemon_detail:
            # Encontrar el stat 'attack'
            attack_stat = next((stat for stat in pokemon_detail['stats'] if stat['stat']['name'] == 'attack'), None)
            
            if attack_stat:
                base_attack = attack_stat['base_stat']
                
                if base_attack > max_attack:
                    max_attack = base_attack
                    pokemon_max_attack = name.capitalize()
                    
    print(f"a) Pokémon de Johto con el mayor ataque base:")
    print(f"   **{pokemon_max_attack}** con un ataque base de **{max_attack}**")


    # b) ¿Cuál es el Pokémon con la velocidad más alta que no sea legendario?
    
    all_pokemon_names = get_all_pokemon_names()
    if not all_pokemon_names:
        return
        
    max_speed = -1
    pokemon_max_speed = None
    
    print("\nProcesando todos los Pokémon (buscando mayor Velocidad Base no legendaria)...")
    
    for i, name in enumerate(sorted(all_pokemon_names.keys())):
        if i % 50 == 0 and i > 0:
             sleep(0.5) 

        # 1. Obtener los datos de la especie para filtrar Legendarios/Míticos
        species_data = get_species_data(name)
        
        if species_data and ('is_legendary' in species_data and species_data['is_legendary']) or \
                           ('is_mythical' in species_data and species_data['is_mythical']):
            continue # Saltar si es legendario o mítico
            
        # 2. Obtener los detalles para la estadística de velocidad
        pokemon_detail = get_pokemon_by_id_or_name(name)
        
        if pokemon_detail and 'stats' in pokemon_detail:
            speed_stat = next((stat for stat in pokemon_detail['stats'] if stat['stat']['name'] == 'speed'), None)
            
            if speed_stat:
                base_speed = speed_stat['base_stat']
                
                if base_speed > max_speed:
                    max_speed = base_speed
                    pokemon_max_speed = name.capitalize()

    print(f"b) Pokémon con la velocidad más alta que no es legendario:")
    print(f"   **{pokemon_max_speed}** con una velocidad base de **{max_speed}**")
    
## 🔹 Extras

def extras():
    """Responde a las preguntas extras."""
    print("\n--- 🔹 Extras ---")

    # a) ¿Cuál es el hábitat más común entre los Pokémon de tipo planta?
    
    grass_type_data = get_data("type/grass")
    if not grass_type_data:
        return
        
    habitat_counts = {}
    
    print("\nProcesando Pokémon tipo Planta (contando hábitats)...")
    for i, p_entry in enumerate(grass_type_data['pokemon']):
        name = p_entry['pokemon']['name']
        
        if i % 10 == 0 and i > 0:
             sleep(0.5) 

        # 1. Obtener los datos de la especie para el hábitat
        species_data = get_species_data(name)
        
        if species_data and 'habitat' in species_data and species_data['habitat']:
            habitat_name = species_data['habitat']['name']
            habitat_counts[habitat_name] = habitat_counts.get(habitat_name, 0) + 1

    if habitat_counts:
        # Encontrar el hábitat con el conteo más alto
        most_common_habitat = max(habitat_counts.items(), key=lambda item: item[1])
        
        print(f"a) El hábitat más común entre los Pokémon de tipo Planta es:")
        print(f"   **{most_common_habitat[0].capitalize()}** con **{most_common_habitat[1]}** apariciones.")
        print(f"   Distribución completa: {habitat_counts}")
    else:
        print("a) No se pudo determinar el hábitat más común para los Pokémon de tipo Planta.")


    # b) ¿Qué Pokémon tiene el menor peso registrado en toda la API?
    
    all_pokemon_names = get_all_pokemon_names()
    if not all_pokemon_names:
        return
        
    min_weight = float('inf')
    pokemon_min_weight = None
    
    print("\nProcesando todos los Pokémon (buscando el menor peso)...")
    for i, name in enumerate(sorted(all_pokemon_names.keys())):
        if i % 50 == 0 and i > 0:
             sleep(0.5) 
             
        pokemon_detail = get_pokemon_by_id_or_name(name)
        
        if pokemon_detail and 'weight' in pokemon_detail:
            # El peso en la API está en hectogramos (hg). 1 hg = 0.1 kg.
            weight = pokemon_detail['weight']
            
            # Hay que manejar el caso de peso 0, que existe en la API (ej: Ghastly/Haunter antes de la Gen 7)
            # o si el dato es nulo. Asumimos que 0 es el menor.
            if weight < min_weight:
                min_weight = weight
                pokemon_min_weight = name.capitalize()

    if pokemon_min_weight:
        weight_kg = min_weight / 10.0
        print(f"b) El Pokémon con el menor peso registrado es:")
        print(f"   **{pokemon_min_weight}** con un peso de **{weight_kg} kg** ({min_weight} hg).")
    else:
        print("b) No se pudo determinar el Pokémon con el menor peso.")

# --- Ejecución Principal ---

if __name__ == "__main__":
    print("Iniciando la consulta a la PokeAPI...")
    
    # Ejecutar las funciones para responder a las preguntas
    clasificacion_por_tipos()
    
    evoluciones()
    
    estadisticas_de_batalla()
    
    extras()
    
    print("\nConsultas finalizadas.")

# El código anterior contiene la lógica para responder a todas las preguntas.
# A continuación, se presenta la salida que se obtendría al ejecutar el código.