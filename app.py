import streamlit as st
import xml.etree.ElementTree as ET
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Nettoyage XML",
    page_icon="🗑️",
    layout="wide"
)

# Titre et description
st.title("🗑️ Suppression automatique des balises Rates")
st.markdown("**Supprime les blocs `<Rates>` avec `rateType='pay'`, `rateStatus='agreed'` et `<Class>Coeff Fixe</Class>`**")

# Upload du fichier XML
uploaded_file = st.file_uploader("📁 Déposez votre fichier XML", type=['xml'])

if uploaded_file is not None:
    try:
        # Lecture du fichier XML
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        
        # Extraire le namespace s'il existe
        namespace = ''
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'
        
        # Debug: afficher le namespace et la structure
        with st.expander("🔧 Debug - Information XML"):
            st.code(f"Namespace détecté: '{namespace}'")
            st.code(f"Root tag: {root.tag}")
            st.code(f"Nombre d'éléments racine: {len(list(root))}")
        
        # Fonction pour chercher avec ou sans namespace
        def find_all_rates(root, namespace):
            if namespace:
                return root.findall(f".//{namespace}Rates")
            else:
                return root.findall(".//Rates")
        
        # Trouver toutes les balises Rates
        all_rates = find_all_rates(root, namespace)
        
        # Si aucune balise trouvée avec namespace, essayer sans
        if len(all_rates) == 0 and namespace:
            all_rates = root.findall(".//Rates")
            namespace = ''
        
        # Si toujours aucune, essayer de parcourir tous les éléments
        if len(all_rates) == 0:
            all_rates = []
            for elem in root.iter():
                if elem.tag.endswith('Rates') or elem.tag == 'Rates':
                    all_rates.append(elem)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de balises <Rates>", len(all_rates))
        
        # Identifier les balises à supprimer
        rates_to_remove = []
        for rates in all_rates:
            rate_type = rates.get('rateType')
            rate_status = rates.get('rateStatus')
            
            # Debug: afficher les attributs
            if len(rates_to_remove) < 3:
                with st.expander(f"🔍 Debug - Rates #{len(rates_to_remove) + 1}"):
                    st.code(f"rateType: {rate_type}")
                    st.code(f"rateStatus: {rate_status}")
                    for child in rates:
                        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        st.code(f"{child_tag}: {child.text}")
            
            # Vérifier si c'est agreed (pay OU bill)
            if rate_status == 'agreed':
                # Chercher Class avec ou sans namespace
                class_elem = None
                if namespace:
                    class_elem = rates.find(f".//{namespace}Class")
                if class_elem is None:
                    class_elem = rates.find(".//Class")
                if class_elem is None:
                    for child in rates:
                        if child.tag.endswith('Class') or child.tag == 'Class':
                            class_elem = child
                            break
                
                if class_elem is not None and class_elem.text:
                    # Nettoyer les espaces avant/après
                    class_text = class_elem.text.strip()
                    if class_text == 'Coeff Fixe':
                        rates_to_remove.append(rates)
        
        with col2:
            st.metric(
                "Balises à supprimer (Coeff Fixe)", 
                len(rates_to_remove), 
                delta=f"-{len(rates_to_remove)}" if len(rates_to_remove) > 0 else "0", 
                delta_color="inverse"
            )
        
        if len(rates_to_remove) > 0:
            st.warning(f"⚠️ {len(rates_to_remove)} balise(s) 'Coeff Fixe' détectée(s) et prête(s) à être supprimée(s)")
            
            # Afficher un aperçu des éléments à supprimer
            with st.expander("🔍 Aperçu des balises qui seront supprimées"):
                for idx, rates in enumerate(rates_to_remove[:5], 1):
                    # Chercher avec namespace si nécessaire
                    if namespace:
                        start_date = rates.find(f".//{namespace}StartDate")
                        amount = rates.find(f".//{namespace}Amount")
                    else:
                        start_date = rates.find(".//StartDate")
                        amount = rates.find(".//Amount")
                    
                    # Fallback: chercher sans namespace
                    if start_date is None:
                        for child in rates.iter():
                            if child.tag.endswith('StartDate'):
                                start_date = child
                            if child.tag.endswith('Amount'):
                                amount = child
                    
                    start_text = start_date.text if start_date is not None else 'N/A'
                    amount_text = amount.text if amount is not None else 'N/A'
                    st.code(
                        f"Bloc {idx}: StartDate={start_text}, Amount={amount_text}", 
                        language="text"
                    )
                if len(rates_to_remove) > 5:
                    st.info(f"... et {len(rates_to_remove) - 5} autre(s)")
            
            if st.button("🗑️ SUPPRIMER LES BALISES", type="primary", use_container_width=True):
                # Suppression des balises
                removed_count = 0
                for rates in rates_to_remove:
                    for parent in root.iter():
                        if rates in list(parent):
                            parent.remove(rates)
                            removed_count += 1
                
                st.success(f"✅ {removed_count} balise(s) supprimée(s) avec succès !")
                
                # Conversion en string XML
                ET.indent(tree, space="  ")
                xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                
                # Afficher statistiques finales
                remaining_rates = len(find_all_rates(root, namespace))
                st.info(f"📊 Balises <Rates> restantes : {remaining_rates}")
                
                # Aperçu du résultat
                with st.expander("📄 Aperçu du XML modifié (50 premières lignes)"):
                    preview = xml_string.decode('utf-8').split('\n')[:50]
                    st.code('\n'.join(preview), language='xml')
                
                # Bouton de téléchargement
                original_filename = uploaded_file.name
                new_filename = original_filename.replace('.xml', '_cleaned.xml')
                
                st.download_button(
                    label="📥 Télécharger le fichier nettoyé",
                    data=xml_string,
                    file_name=new_filename,
                    mime="application/xml",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.success("✅ Aucune balise 'Coeff Fixe' à supprimer dans ce fichier !")
            
    except ET.ParseError as e:
        st.error(f"❌ Erreur de parsing XML : {str(e)}")
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        import traceback
        st.code(traceback.format_exc())
else:
    st.info("👆 Veuillez uploader un fichier XML pour commencer")
    
    # Instructions
    with st.expander("ℹ️ Comment utiliser cette application"):
        st.markdown("""
        1. **Uploadez** votre fichier XML
        2. L'application détecte automatiquement les balises `<Rates>` avec :
           - `rateType="pay"` ou `rateType="bill"`
           - `rateStatus="agreed"`
           - `<Class>Coeff Fixe</Class>`
        3. Cliquez sur **SUPPRIMER LES BALISES**
        4. **Téléchargez** le fichier nettoyé
        """)
