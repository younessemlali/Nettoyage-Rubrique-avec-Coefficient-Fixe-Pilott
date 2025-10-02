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
        
        # Trouver toutes les balises Rates
        all_rates = root.findall(".//Rates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de balises <Rates>", len(all_rates))
        
        # Identifier les balises à supprimer
        rates_to_remove = []
        for rates in all_rates:
            rate_type = rates.get('rateType')
            rate_status = rates.get('rateStatus')
            
            # Vérifier si c'est agreed (pay OU bill)
            if rate_status == 'agreed':
                # Vérifier si contient <Class>Coeff Fixe</Class>
                class_elem = rates.find('.//Class')
                if class_elem is not None and class_elem.text:
                    # Nettoyer les espaces avant/après
                    class_text = class_elem.text.strip()
                    if class_text == 'Coeff Fixe':
                        rates_to_remove.append(rates)
        
        with col2:
            st.metric(
                "Balises à supprimer (Coeff Fixe)", 
                len(rates_to_remove), 
                delta=f"-{len(rates_to_remove)}", 
                delta_color="inverse"
            )
        
        if len(rates_to_remove) > 0:
            st.warning(f"⚠️ {len(rates_to_remove)} balise(s) 'Coeff Fixe' détectée(s) et prête(s) à être supprimée(s)")
            
            # Afficher un aperçu des éléments à supprimer
            with st.expander("🔍 Aperçu des balises qui seront supprimées"):
                for idx, rates in enumerate(rates_to_remove[:5], 1):
                    start_date = rates.find('.//StartDate')
                    amount = rates.find('.//Amount')
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
                remaining_rates = len(root.findall(".//Rates"))
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
else:
    st.info("👆 Veuillez uploader un fichier XML pour commencer")
    
    # Instructions
    with st.expander("ℹ️ Comment utiliser cette application"):
        st.markdown("""
        1. **Uploadez** votre fichier XML
        2. L'application détecte automatiquement les balises `<Rates>` avec :
           - `rateType="pay"`
           - `rateStatus="agreed"`
           - `<Class>Coeff Fixe</Class>`
        3. Cliquez sur **SUPPRIMER LES BALISES**
        4. **Téléchargez** le fichier nettoyé
        """)
