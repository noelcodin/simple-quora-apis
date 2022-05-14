1.Update application config `common/config.py`
- Update `HOST` and `PORT` to run the app on a different server and port
- Update `mysqlConn` as the actual db connection info
- Update `KEYFILE` and `CERTFILE` to your own ssl certification files

2.Table creation
- Make sure the db name specified in `mysqlConn` actual exists on server
- Tables used by application will be auto-created once the app is launched

3.Setup python environment  
`python -m pip install -r requirements.txt`

4.Lauch application  
- For test  
`python run_debug.py`

- For production  
`python run_multi_process.py`

5.Api documentation  
- It's hosted on the app server.  
- Check it in `https://${HOST}:${PORT}/docs/api/`.  

6.Api automation test  
`python -m pytest -v tests --html=report\report.html --self-contained-html`
