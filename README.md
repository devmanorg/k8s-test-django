# Django site

Докеризированный сайт на Django для экспериментов с Kubernetes.

Внутри конейнера Django запускается с помощью Nginx Unit, не путать с Nginx. Сервер Nginx Unit выполняет сразу две функции: как веб-сервер он раздаёт файлы статики и медиа, а в роли сервера-приложений он запускает Python и Django. Таким образом Nginx Unit заменяет собой связку из двух сервисов Nginx и Gunicorn/uWSGI. [Подробнее про Nginx Unit](https://unit.nginx.org/).

## Как запустить dev-версию

Запустите базу данных и сайт:

```shell-session
$ docker-compose up
```

В новом терминале не выключая сайт запустите команды для настройки базы данных:

```shell-session
$ docker-compose run web ./manage.py migrate  # создаём/обновляем таблицы в БД
$ docker-compose run web ./manage.py createsuperuser
```

Для тонкой настройки Docker Compose используйте переменные окружения. Их названия отличаются от тех, что задаёт docker-образа, сделано это чтобы избежать конфликта имён. Внутри docker-compose.yaml настраиваются сразу несколько образов, у каждого свои переменные окружения, и поэтому их названия могут случайно пересечься. Чтобы не было конфликтов к названиям переменных окружения добавлены префиксы по названию сервиса. Список доступных переменных можно найти внутри файла [`docker-compose.yml`](./docker-compose.yml).

## Переменные окружения

Образ с Django считывает настройки из переменных окружения:

`SECRET_KEY` -- обязательная секретная настройка Django. Это соль для генерации хэшей. Значение может быть любым, важно лишь, чтобы оно никому не было известно. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key).

`DEBUG` -- настройка Django для включения отладочного режима. Принимает значения `TRUE` или `FALSE`. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-DEBUG).

`ALLOWED_HOSTS` -- настройка Django со списком разрешённых адресов. Если запрос прилетит на другой адрес, то сайт ответит ошибкой 400. Можно перечислить несколько адресов через запятую, например `127.0.0.1,192.168.0.1,site.test`. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts).

`DATABASE_URL` -- адрес для подключения к базе данных PostgreSQL. Другие СУБД сайт не поддерживает. [Формат записи](https://github.com/jacobian/dj-database-url#url-schema).


# Работа в Kubernetes

1) Для работы в kubernetes требуется создать кластер, в данном уроке в роли кластера
выступает minikibe. Для его установки потребуется virtualbox, [kubectl](https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/), [minikube](https://minikube.sigs.k8s.io/docs/drivers/virtualbox/)
2) Для того что бы создать pod, воспользуйтесь командой:
```sh
kubectl run --image=имя_докеробраза имя_пода --port=80
```
3) Что бы развернуть django проект на k8s.Нужно проделать следуюшие манипуляции:
    1. Установить postgres и создать базу данных локально
    2. Установить postgres в кластере minikube [по этому туториалу](https://artifacthub.io/packages/helm/bitnami/postgresql)
    в качестве параметров вам нужно прописать: `--set global.postgresql.auth.database=db_name`,
    `--set global.postgresql.auth.username=db_user`
   `--set global.postgresql.auth.password=db_password`
   3. Пробросить порты для базы данных этой командой:
    ```sh
    kubectl port-forward --namespace default svc/postgres_name 5432:5432
    ```
   4. Создать под c django проектом и так же пробросить порт для этого пода:
      1) Создать yaml-файл со своими конфидиенциальными данными(SECRET_KEY,DB_PASSWORD, etc.) 
         ```sh 
         apiVersion: v1
         kind: Secret
         metadata:
           name: mysecret
         type: Opaque
         stringData:
             SECRET_KEY: "replace_me"
             DATABASE_URL: "postgres://test_k8s:test_k8s@psql-test-postgresql:5432/test_k8s"
             POSTGRES_DB: "test_k8s"
             POSTGRES_USER: "test_k8s"
             POSTGRES_PASSWORD: "test_k8s"
         ```
      2) Применить секрет  командами:
           ```sh 
          kubectl apply -f secret_name.yaml
          kubectl get secret mysecret -o yaml - покажет зашифрованные переменные
           ```
      3) kubectl port-forward name_pod host_port:pod_port
   
   5. Перейти в браузере по локальному адресу и порту который был указан в 4 шаге
Это самые начальные  операции для разворачивания проекта на Kubernetes.