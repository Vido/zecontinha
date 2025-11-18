from django import forms

class TradeForm(forms.Form):

    pair = forms.CharField(
        #widget=forms.HiddenInput()
        )

    pair_stats_id = forms.CharField(
        widget=forms.HiddenInput()
    )

    periodo = forms.IntegerField(
        label='Número de Periodos',
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'form_periodo',
            'min_value': '40',
            'step': '20'})
        )

    qnt_x = forms.IntegerField(
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

    qnt_y = forms.IntegerField(
        label='Qnt.Y',
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


class ExitTradeForm(forms.Form):

    trade_id = forms.CharField(
        widget=forms.HiddenInput()
    )

    exit_x = forms.FloatField(
        label='Preço X',
        #default=0.1,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'form_exit_x',
            'step': '0.01',
            'max_value': '1000.0',
            'min_value': '0.1',
            'initial': '1.0'})
        )

    exit_y = forms.FloatField(
        label='Preço Y',
        #default=0.1,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'form_exit_x',
            'step': "0.01",
            'max_value': '1000.0',
            'min_value': '0.1',
            'initial': '1.0'})
        )