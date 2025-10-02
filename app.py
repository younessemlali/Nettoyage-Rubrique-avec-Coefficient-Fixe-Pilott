import streamlit as st
import xml.etree.ElementTree as ET
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Nettoyage XML",
    page_icon="🗑️",
    layout="wide"
)

# Enregistrer les namespaces pour les préserver
ET.register_namespace('', 'http://ns.hr-xml.org/2007-04-15')

# Titre et description
st.title("🗑️ Suppression automatique des balises Rates")
st.markdown("**Supprime les blocs `<Rates>` avec `rateStatus='agreed'` et `<Class>Coeff Fixe</Class>`**")

# Upload du fichier XML
uploaded_file = st.file_uploader("📁 Déposez votre fichier XML", type=['xml'])

if uploaded_file is not None:
    try:
        # Lire le contenu original pour préserver le format
        content = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Parser le XML
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        
        # Détecter le namespace
        ns = {'hr': 'http://ns.hr-xml.org/2007-04-15'}
        
        # Trouver toutes les balises Rates avec namespace
        all_rates = root.findall('.//{http://ns.hr-xml.org/2007-04-15}Rates')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de balises <Rates>", len(all_rates))
        
        # Identifier les balises à supprimer
        rates_to_remove = []
        for rates in all_rates:
            rate_status = rates.get('rateStatus')
            
            # Vérifier si c'est agreed
            if rate_status == 'agreed':
                # Chercher <Class>Coeff Fixe</Class>
                class_elem = rates.find('{http://ns.hr-xml.org/2007-04-15}Class')
                
                if class_elem is not None and class_elem.text:
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
            st.warning(f"⚠️ {len(rates_to_remove)} balise(s) 'Coeff Fixe' détectée(s)")
            
            # Aperçu des éléments à supprimer
            with st.expander("🔍 Aperçu des balises qui seront supprimées"):
                for idx, rates in enumerate(rates_to_remove[:5], 1):
                    start_date = rates.find('{http://ns.hr-xml.org/2007-04-15}StartDate')
                    amount = rates.find('{http://ns.hr-xml.org/2007-04-15}Amount')
                    
                    start_text = start_date.text if start_date is not None else 'N/A'
                    amount_text = amount.text if amount is not None else 'N/A'
                    st.code(f"Bloc {idx}: StartDate={start_text}, Amount={amount_text}")
                    
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
                
                st.success(f"✅ {removed_count} balise(s) supprimée(s) !")
                
                # Écrire le XML en préservant le format original
                xml_bytes = BytesIO()
                tree.write(xml_bytes, encoding='utf-8', xml_declaration=True, method='xml')
                xml_string = xml_bytes.getvalue()
                
                # Statistiques finales
                remaining_rates = len(root.findall('.//{http://ns.hr-xml.org/2007-04-15}Rates'))
                st.info(f"📊 Balises <Rates> restantes : {remaining_rates}")
                
                # Aperçu
                with st.expander("📄 Aperçu du XML (50 premières lignes)"):
                    preview = xml_string.decode('utf-8').split('\n')[:50]
                    st.code('\n'.join(preview), language='xml')
                
                # Téléchargement
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
            st.success("✅ Aucune balise 'Coeff Fixe' à supprimer !")
            
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        import traceback
        st.code(traceback.format_exc())
else:
    st.info("👆 Veuillez uploader un fichier XML")
    
    with st.expander("ℹ️ Mode d'emploi"):
        st.markdown("""
        1. **Uploadez** votre fichier XML
        2. Vérifiez les balises détectées
        3. Cliquez sur **SUPPRIMER LES BALISES**
        4. **Téléchargez** le fichier nettoyé
        """)
