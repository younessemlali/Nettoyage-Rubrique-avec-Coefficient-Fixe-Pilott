import streamlit as st
import re

# Configuration de la page
st.set_page_config(
    page_title="Nettoyage XML",
    page_icon="🗑️",
    layout="wide"
)

# Titre
st.title("🗑️ Suppression automatique des groupes Rates")
st.markdown("**Supprime les groupes de balises `<Rates>` (pay + bill) contenant `<Class>Coeff Fixe</Class>`**")

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
        
        # Pattern pour capturer les GROUPES de 2 balises Rates consécutives avec Coeff Fixe
        # On cherche: <Rates rateType="pay"...>...</Rates> suivi de <Rates rateType="bill"...>...</Rates>
        # où les deux contiennent <Class>Coeff Fixe</Class>
        pattern = r'(<Rates\s+rateType="pay"[^>]*>.*?</Rates>)\s*(<Rates\s+rateType="bill"[^>]*>.*?</Rates>)'
        
        all_groups = list(re.finditer(pattern, content, re.DOTALL))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Groupes pay+bill détectés", len(all_groups))
        
        # Identifier les groupes qui contiennent "Coeff Fixe" dans LES DEUX balises
        groups_to_remove = []
        for match in all_groups:
            pay_bloc = match.group(1)
            bill_bloc = match.group(2)
            
            # Vérifier si les DEUX blocs contiennent "Coeff Fixe"
            has_coeff_fixe_pay = '<Class>Coeff Fixe</Class>' in pay_bloc or '<Class> Coeff Fixe </Class>' in pay_bloc
            has_coeff_fixe_bill = '<Class>Coeff Fixe</Class>' in bill_bloc or '<Class> Coeff Fixe </Class>' in bill_bloc
            
            if has_coeff_fixe_pay and has_coeff_fixe_bill:
                groups_to_remove.append(match)
        
        with col2:
            st.metric(
                "Groupes à supprimer (Coeff Fixe)", 
                len(groups_to_remove),
                delta=f"-{len(groups_to_remove) * 2} balises" if len(groups_to_remove) > 0 else "0",
                delta_color="inverse"
            )
        
        if len(groups_to_remove) > 0:
            st.warning(f"⚠️ {len(groups_to_remove)} groupe(s) 'Coeff Fixe' détecté(s) ({len(groups_to_remove) * 2} balises au total)")
            
            # Aperçu
            with st.expander("🔍 Aperçu des groupes à supprimer"):
                for i, match in enumerate(groups_to_remove[:5], 1):
                    pay_bloc = match.group(1)
                    bill_bloc = match.group(2)
                    
                    # Extraire infos du bloc pay
                    start_pay = re.search(r'<StartDate>([^<]+)</StartDate>', pay_bloc)
                    amount_pay = re.search(r'<Amount[^>]*>([^<]+)</Amount>', pay_bloc)
                    
                    # Extraire infos du bloc bill
                    amount_bill = re.search(r'<Amount[^>]*>([^<]+)</Amount>', bill_bloc)
                    
                    st.code(f"""Groupe {i}:
  - PAY:  StartDate={start_pay.group(1) if start_pay else 'N/A'}, Amount={amount_pay.group(1) if amount_pay else 'N/A'}
  - BILL: Amount={amount_bill.group(1) if amount_bill else 'N/A'}""")
                    
                if len(groups_to_remove) > 5:
                    st.info(f"... et {len(groups_to_remove) - 5} autre(s) groupe(s)")
            
            if st.button("🗑️ SUPPRIMER LES GROUPES", type="primary", use_container_width=True):
                # Supprimer les groupes en partant de la fin pour ne pas décaler les indices
                modified_content = content
                
                # Trier les matches par position (du plus loin au plus proche)
                sorted_matches = sorted(groups_to_remove, key=lambda m: m.start(), reverse=True)
                
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
                    
                    # Chercher si on doit aussi supprimer la ligne suivante (si vide)
                    if end < len(modified_content) and modified_content[end:end+1] == '\n':
                        end += 1
                    
                    # Supprimer le groupe entier (pay + bill)
                    modified_content = modified_content[:start] + modified_content[end:]
                
                st.success(f"✅ {len(groups_to_remove)} groupe(s) supprimé(s) ({len(groups_to_remove) * 2} balises) !")
                
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
            st.success("✅ Aucun groupe 'Coeff Fixe' à supprimer !")
            
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        import traceback
        st.code(traceback.format_exc())
else:
    st.info("👆 Veuillez uploader un fichier XML")
    
    with st.expander("ℹ️ Mode d'emploi"):
        st.markdown("""
        1. **Uploadez** votre fichier XML
        2. Vérifiez les groupes détectés
        3. Cliquez sur **SUPPRIMER LES GROUPES**
        4. **Téléchargez** le fichier nettoyé
        
        ⚠️ **Important** : Ce script supprime les GROUPES de 2 balises consécutives :
        - Une balise `<Rates rateType="pay">` avec `<Class>Coeff Fixe</Class>`
        - Suivie d'une balise `<Rates rateType="bill">` avec `<Class>Coeff Fixe</Class>`
        
        Les deux balises du groupe doivent contenir "Coeff Fixe" pour être supprimées.
        """)
