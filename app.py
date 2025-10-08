import streamlit as st
import re

# Configuration de la page
st.set_page_config(
    page_title="Nettoyage XML",
    page_icon="🗑️",
    layout="wide"
)

# Titre
st.title("🗑️ Suppression automatique des balises Rates")
st.markdown("**Supprime tous les blocs `<Rates>` contenant `<Class>Coeff Fixe</Class>` (pay et bill)**")

# Upload
uploaded_file = st.file_uploader("📂 Déposez votre fichier XML", type=['xml'])

if uploaded_file is not None:
    try:
        # Lire le contenu brut avec détection automatique de l'encodage
        raw_content = uploaded_file.read()
        
        # Essayer différents encodages
        content = None
        for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']:
            try:
                content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            st.error("❌ Impossible de décoder le fichier. Encodage non supporté.")
            st.stop()
        
        # Pattern pour capturer TOUS les blocs <Rates>...</Rates>
        pattern = r'<Rates[^>]*>.*?</Rates>'
        all_rates_matches = list(re.finditer(pattern, content, re.DOTALL))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de balises <Rates>", len(all_rates_matches))
        
        # Identifier ceux qui contiennent "Coeff Fixe"
        rates_to_remove = []
        for match in all_rates_matches:
            bloc = match.group(0)
            if '<Class>Coeff Fixe</Class>' in bloc or '<Class> Coeff Fixe </Class>' in bloc:
                rates_to_remove.append(match)
        
        with col2:
            st.metric(
                "Balises à supprimer (Coeff Fixe)", 
                len(rates_to_remove),
                delta=f"-{len(rates_to_remove)}" if len(rates_to_remove) > 0 else "0",
                delta_color="inverse"
            )
        
        if len(rates_to_remove) > 0:
            st.warning(f"⚠️ {len(rates_to_remove)} balise(s) 'Coeff Fixe' détectée(s)")
            
            # Aperçu avec détection du type (pay/bill)
            with st.expander("🔍 Aperçu des balises à supprimer"):
                for i, match in enumerate(rates_to_remove[:10], 1):
                    bloc = match.group(0)
                    # Extraire le type
                    type_match = re.search(r'rateType="([^"]+)"', bloc)
                    rate_type = type_match.group(1) if type_match else 'N/A'
                    # Extraire StartDate et Amount
                    start_match = re.search(r'<StartDate>([^<]+)</StartDate>', bloc)
                    amount_match = re.search(r'<Amount[^>]*>([^<]+)</Amount>', bloc)
                    start = start_match.group(1) if start_match else 'N/A'
                    amount = amount_match.group(1) if amount_match else 'N/A'
                    st.code(f"Bloc {i}: Type={rate_type}, StartDate={start}, Amount={amount}")
                if len(rates_to_remove) > 10:
                    st.info(f"... et {len(rates_to_remove) - 10} autre(s)")
            
            if st.button("🗑️ SUPPRIMER LES BALISES", type="primary", use_container_width=True):
                # Supprimer les blocs en partant de la fin pour ne pas décaler les indices
                modified_content = content
                
                # Trier les matches par position (du plus loin au plus proche)
                sorted_matches = sorted(rates_to_remove, key=lambda m: m.start(), reverse=True)
                
                for match in sorted_matches:
                    start = match.start()
                    end = match.end()
                    
                    # Trouver le début de la ligne pour garder l'indentation propre
                    line_start = modified_content.rfind('\n', 0, start)
                    if line_start != -1:
                        # Vérifier si entre line_start et start il n'y a que des espaces
                        between = modified_content[line_start:start]
                        if between.strip() == '':
                            start = line_start
                    
                    # Supprimer le bloc
                    modified_content = modified_content[:start] + modified_content[end:]
                
                st.success(f"✅ {len(rates_to_remove)} balise(s) supprimée(s) !")
                
                # Compter les Rates restants
                remaining = len(re.findall(r'<Rates[^>]*>', modified_content))
                st.info(f"📊 Balises <Rates> restantes : {remaining}")
                
                # Aperçu
                with st.expander("📄 Aperçu du XML modifié (50 premières lignes)"):
                    preview_lines = modified_content.split('\n')[:50]
                    st.code('\n'.join(preview_lines), language='xml')
                
                # Téléchargement
                original_filename = uploaded_file.name
                new_filename = original_filename.replace('.xml', '_cleaned.xml')
                
                st.download_button(
                    label="📥 Télécharger le fichier nettoyé",
                    data=modified_content.encode('utf-8'),
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
        2. Vérifiez les balises détectées (pay + bill)
        3. Cliquez sur **SUPPRIMER LES BALISES**
        4. **Téléchargez** le fichier nettoyé
        
        ⚠️ **Important** : Ce script supprime TOUTES les balises `<Rates>` 
        contenant `<Class>Coeff Fixe</Class>`, qu'elles soient de type 
        "pay" ou "bill".
        """)
