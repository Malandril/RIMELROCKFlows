import os, sys
import subprocess

def listDirectory(path):
    tmp = os.listdir(path)
    for i in range(len(tmp)): 
        tmp[i] = path + tmp[i]
    return tmp

def isMavenProject(listOfDirectories):
    '''
        listOfDirection : List
    '''
    res = {}
    for directory in listOfDirectories:
        if(os.path.isdir(directory)):
            res[directory] = False
            for nameOfFile in os.listdir(directory):
                if("pom.xml" in nameOfFile):
                    res[directory] = True
    return res

def processingSonar(listOfDirectories):
    '''
        listOfDirection : Dictionnary
    '''
    for directory in listOfDirectories:
        if(listOfDirectories[directory]):
            execSonarMaven(directory)
        else:
            execSonar(directory)

def nameSonarProject(path):
    index = path.rfind('/') +1
    return path[index:]

def execSonar(directory):
    projectName = "-Dsonar.projectKey=" + nameSonarProject(directory)
    print("\n------------------------------------------------")
    print("PROCESSING SONAR-SCANNER projectKey=" + projectName)
    print("------------------------------------------------")
    subprocess.run(["sonar-scanner", projectName, "-Dsonar.sources=."]) 

def execSonarMaven(directory):
    os.chdir(directory)
    print("\n------------------------------------------------")
    print("PROCESSING SONAR WITH MAVEN FROM " + os.getcwd())
    print("------------------------------------------------\n")
    subprocess.run(["mvn", "clean", "install"]) 
    subprocess.run(["mvn", "sonar:sonar"])

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        print("Please specify the directory to analyse.")
    else:
        directory = sys.argv[1]
        if (not(os.path.isdir(directory))):
            print("Is not a directory !")
        else :
            tmp = listDirectory(directory)
            #print(listDirectory(directory)) #OK
            #print(isMavenProject(tmp)) #OK
            processingSonar(isMavenProject(tmp))
