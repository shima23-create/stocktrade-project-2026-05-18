from django import forms

class ContactForm(forms.Form):
    # フォームのフィールドをクラス変数として定義
    # CharField = 文字列
    # EmailField = メールアドレス用の文字列
    name = forms.CharField(label='お名前')
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='件名')
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # nameフィールドのplaceholderにメッセージを登録
        # フォームに表示される薄い文字
        self.fields['name'].widget.attrs['placeholder'] = 'お名前を入力してください'
        
        # nameフィールドを出力する<input>タグのclass属性を設定
        self.fields['name'].widget.attrs['class'] = 'form-control'
        
        # emailフィールドのplaceholderにメッセージを登録
        # フォームに表示される薄い文字
        self.fields['email'].widget.attrs['placeholder'] = \
          'メールアドレスを入力してください'
        
        # emailフィールドを出力する<input>タグのclass属性を設定
        self.fields['email'].widget.attrs['class'] = 'form-control'
        
        # titleフィールドのplaceholderにメッセージを登録
        # フォームに表示される薄い文字
        self.fields['title'].widget.attrs['placeholder'] = \
          'タイトルを入力してください'
        
        # titleフィールドを出力する<input>タグのclass属性を設定
        self.fields['title'].widget.attrs['class'] = 'form-control'
        
        # messageフィールドのplaceholderにメッセージを登録
        # フォームに表示される薄い文字
        self.fields['message'].widget.attrs['placeholder'] = \
          'メッセージを入力してください'
        
        # messageフィールドを出力する<input>タグのclass属性を設定
        self.fields['message'].widget.attrs['class'] = 'form-control'