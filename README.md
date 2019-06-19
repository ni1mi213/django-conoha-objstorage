# django-conoha-objstorage
django-conoha-objstorageは、DjangoのFileFiledをConohaオブジェクトストレージに保存ためのライブラリです。

## Quickstart
setting.pyに下記の内容を設定してください。

```python
INSTALLED_APPS = [
    'django_conoha_objstorage',
    ...
]
```

```python
OS_TENANT_NAME = 'YOUR_TENANT_NAME'
OS_TENANT_ID = 'YOUR_TENANT_ID'
OS_USERNAME = 'YOUR_USERNAME'
OS_PASSWORD = 'YOUR_PASSWORD'
OS_AUTH_URL = 'YOUR_AUTH_URL'
OS_ENDPOINT_URL = 'YOUR_ENDPOINT_URL'
OS_TEMPURL_KEY = 'YOUR_TEMPURL_KEY'

```

```python
DEFAULT_FILE_STORAGE = 'django_conoha_objstorage.backend.ConohaObjectStorage'
DEFAULT_CONTAINER = 'your_container_name'
```

これでdjango-conoha-objstorageを使う準備ができました。


## Define the model
FileFiledをのカラムを持つモデルを定義します。
```python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=255)
    object = models.FileField(upload_to='your_container_name')
```
あとは保存するだけで`upload_to`に指定したcontainerにファイルが保存されます。

## Usage of abstract base class
django_conoha_objstorage.modelsに抽象基底クラスがあります。使用方法は、your_app/models.pyに下記を追加してください。
```python
from django_conoha_objstorage.models import (
    BaseObjectStorage,
    get_upload_container,
    create_choice_tuple,
)
```

それぞれの機能を紹介します。  
### BaseObjectStorage
object, container_nameが実装してあります。適宜オーバーライドしてください。  
尚、このモデルを継承するとデータ削除時に、ファイルも合わせて削除してくれます。（一括削除を含む）

### get_upload_container
objectの`upload_to`にcontainer_nameの値を返します。適宜オーバーライドしてください。

### create_choice_tuple
container_nameに`choice=create_choice_tuple`を指定すると`swift list`で返ってくるコンテナのリストからタプルを作成します。
