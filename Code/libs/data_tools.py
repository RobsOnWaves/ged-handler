import uuid
import pandas as pd
import warnings
class DataTools:

    def __init__(self):
        #waiting for needing parameters
        pass

    @staticmethod
    def generer_nom_fichier_unique_uuid(prefixe='dataframe_', suffixe='.h5'):
        unique_id = uuid.uuid4()  # Générer un UUID unique
        nom_fichier = f"{prefixe}{unique_id}{suffixe}"
        return nom_fichier

    @staticmethod
    def store_df_to_file(df, chemin_fichier='dataframes.h5', cle='df_'):
        # Ouvrir le fichier HDF5 en mode append pour ajouter des données
        with pd.HDFStore(chemin_fichier, mode='a') as store:
            # Générer une clé unique pour le nouveau dataframe
            # En utilisant le nombre de dataframes déjà présents dans le fichier
            n_dataframes = len(store.keys())
            nouvelle_cle = f'{cle}{n_dataframes + 1}'

            # Stocker le nouveau dataframe dans le fichier sous la nouvelle clé
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                store.put(nouvelle_cle, df, format='fixed')

        # Renvoyer le chemin d'accès au fichier
        return chemin_fichier