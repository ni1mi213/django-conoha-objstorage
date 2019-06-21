# django-conoha-objstorage
django-conoha-objstorageは、DjangoのFileFiledをConohaオブジェクトストレージに保存ためのライブラリです。

## Quickstart
setting.pyに下記の内容を設定してください。

`INSTALLED_APPS`にdjango_conohoa_objstorageを追加します。
```python
INSTALLED_APPS = [
      'django_conoha_objstorage',
      ...
      ]
```

環境変数にテナント情報を設定します。
```python
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

OS_TENANT_NAME = os.environ['OS_TENANT_NAME']
OS_TENANT_ID = os.environ['OS_TENANT_ID']
OS_USERNAME = os.environ['OS_USERNAME']
OS_PASSWORD = os.environ['OS_PASSWORD']
OS_AUTH_URL = os.environ['OS_AUTH_URL']
OS_ENDPOINT_URL = os.environ['OS_ENDPOINT_URL']
OS_TEMPURL_KEY = os.environ['OS_TEMPURL_KEY']
```

使用するSTORAGEとデフォルトのコンテナを指定します。
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
