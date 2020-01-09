from django import forms

class TradeForm(forms.Form):

    pair_stats_id = forms.CharField(
        #widget=forms.HiddenInput()
        )

    qnt_x = forms.CharField(
        label='Qnt.X',
        #default=0.1,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'form_qntx',
            'min_value': '0',
            'step': '1'})
        )
    entry_x = forms.FloatField(
        label='Preço X',
        #default=0.1,
        required=True,

        widget=forms.NumberInput(attrs={
            'id': 'form_entry_x',
            'step': '0.01',
            'max_value': '1000.0',
            'min_value': '0.1',
            'initial': '1.0'})
        )
    qnt_y = forms.CharField(
        label='Qnt.X',
        #default=0.1,
        required=True,

        widget=forms.NumberInput(attrs={
            'id': 'form_qnty',
            'step': "1",
            'min_value': '0'})
        )
    entry_y = forms.FloatField(
        label='Preço Y',
        #default=0.1,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'form_entry_y',
            'step': "0.01",
            'max_value': '1000.0',
            'min_value': '0.1',
            'initial': '1.0'})
        )