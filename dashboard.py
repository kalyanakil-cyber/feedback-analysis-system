import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title='Feedback Analysis System', layout='wide')
st.title('Intelligent User Feedback Analysis System')
st.markdown('### Capstone Project Dashboard')
st.divider()
tickets_file = 'output/generated_tickets.csv'
log_file = 'output/processing_log.csv'
df = pd.read_csv(tickets_file) if os.path.exists(tickets_file) else pd.DataFrame()
log_df = pd.read_csv(log_file) if os.path.exists(log_file) else pd.DataFrame()

tab1, tab2, tab3 = st.tabs(['Dashboard', 'Tickets', 'Processing Log'])

with tab1:
    st.subheader('System Overview')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Tickets', len(df))
    col2.metric('Bugs', len(df[df['category']=='Bug']) if not df.empty and 'category' in df.columns else 0)
    col3.metric('Feature Requests', len(df[df['category']=='Feature Request']) if not df.empty and 'category' in df.columns else 0)
    col4.metric('Avg Quality', round(pd.to_numeric(df['quality_score'], errors='coerce').mean(), 1) if not df.empty else 0)
    st.divider()
    if not df.empty and 'category' in df.columns:
        st.subheader('Category Distribution')
        col1, col2 = st.columns(2)
        col1.bar_chart(df['category'].value_counts())
        col2.bar_chart(df['priority'].value_counts()) if 'priority' in df.columns else None
    else:
        st.info('No data yet. Run the pipeline first!')

with tab2:
    st.subheader('Generated Tickets')
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.subheader('Ticket Details')
        selected = st.selectbox('Select ticket', df['ticket_id'].tolist())
        row = df[df['ticket_id']==selected].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.write('**ID:**', row.get('ticket_id','N/A'))
            st.write('**Category:**', row.get('category','N/A'))
            st.write('**Priority:**', row.get('priority','N/A'))
        with col2:
            st.write('**Quality Score:**', row.get('quality_score','N/A'))
            st.write('**Source:**', row.get('source_id','N/A'))
            st.write('**Processed:**', row.get('processed_at','N/A'))
        st.write('**Title:**', row.get('suggested_title','N/A'))
        st.write('**Description:**', row.get('ticket_description','N/A'))
    else:
        st.info('No tickets yet!')

with tab3:
    st.subheader('Processing Log')
    if not log_df.empty:
        col1, col2 = st.columns(2)
        col1.metric('Successful', len(log_df[log_df['status']=='SUCCESS']) if 'status' in log_df.columns else 0)
        col2.metric('Errors', len(log_df[log_df['status']=='ERROR']) if 'status' in log_df.columns else 0)
        st.dataframe(log_df, use_container_width=True)
    else:
        st.info('No log yet!')

st.divider()
st.subheader('Manual Override')
st.write('Edit any ticket directly below and save changes.')
if not df.empty and 'ticket_id' in df.columns:
    override_ticket = st.selectbox('Select ticket to edit', df['ticket_id'].tolist(), key='override_select')
    override_row = df[df['ticket_id']==override_ticket].iloc[0]
    col1, col2 = st.columns(2)
    with col1:
        new_category = st.selectbox('Category', ['Bug','Feature Request','Praise','Complaint','Spam'], index=['Bug','Feature Request','Praise','Complaint','Spam'].index(override_row.get('category','Bug')) if override_row.get('category','Bug') in ['Bug','Feature Request','Praise','Complaint','Spam'] else 0)
        new_priority = st.selectbox('Priority', ['Critical','High','Medium','Low'], index=['Critical','High','Medium','Low'].index(override_row.get('priority','Medium')) if override_row.get('priority','Medium') in ['Critical','High','Medium','Low'] else 2)
    with col2:
        new_title = st.text_input('Title', value=str(override_row.get('suggested_title','')))
        new_description = st.text_area('Description', value=str(override_row.get('ticket_description','')))
    if st.button('Save Changes', type='primary'):
        df.loc[df['ticket_id']==override_ticket, 'category'] = new_category
        df.loc[df['ticket_id']==override_ticket, 'priority'] = new_priority
        df.loc[df['ticket_id']==override_ticket, 'suggested_title'] = new_title
        df.loc[df['ticket_id']==override_ticket, 'ticket_description'] = new_description
        df.to_csv('output/generated_tickets.csv', index=False)
        st.success('Ticket updated successfully!')
        st.rerun()
else:
    st.info('No tickets available to edit.')
