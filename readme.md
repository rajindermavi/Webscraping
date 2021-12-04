# Tech stacks

The docker container will output 
    1. A json with tech stacks of websites for the NC survey.  
    
Format:

{... url:{category1:["tech1","tech2",...],category2:["techa1","techa2",...] } }


Find the CSV on [google sheets](https://docs.google.com/spreadsheets/d/1oOBfaKLSQAeOB4V7gwjQYyeOdz6a5IBmkH_Lr2Kzn40/edit?usp=sharing)

## Commands:
```
docker build -t selenium_image .

docker container  run -it --name selenium_container selenium_image

docker cp selenium_container:/app/survey_techs.json survey_techs.json

```
