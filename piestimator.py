from Tkinter import *
from docclass import *
from bs4 import BeautifulSoup
import urllib2
import re


class FacultyMember(object):
    """docstring for FacultyMember"""

    def __init__(self, name, url, publications=[]):
        self.name = name    # Faculty member name
        self.profile_url = url  # url ofaculty member
        self.publications = publications    # publications list empty as a default


class ResearchProject(object):
    """docstring for ResearchProject"""

    def __init__(self, title, summary, piname):
        self.title = title      # Research Project title
        self.summary = summary  # Research Project summary
        self.piname = piname    # Principal Investigator name


class Predictor(object):
    """docstring for Predictor"""

    def __init__(self):
        self.classifier = naivebayes(getwords)  # Naive Bayes obj
        self.faculty_members = {}   # key=faculty member name, value=faculty member object
        self.projects = {}  # key=project title value=research project obj

    def fetch_members(self, link_):
        contents = urllib2.urlopen(link_).read()  # to open link and read the content
        soup = BeautifulSoup(contents, 'html.parser')  # to parse it using BeautifulSoup
        new_link = 'http://cs.sehir.edu.tr'     # link to the join with members' link
        for member in soup.find_all('div', class_='member'):    # to take each member
            href = member.find('a').get('href').encode('utf8').split('/')   # getting href
            name = [eval(repr(i.strip().encode('utf8'))) for i in member.find('h4').stripped_strings] # to take name
            self.name = name[0].split()[0] + ' ' + name[0].split()[-1]  # take name and surname
            self.href = new_link + '/'.join(href[:-2]) + '/' + name[0].split()[0] + '-' + name[0].split()[-1] # join link
            self.publications = self.fetch_publications(self.href)  # to take publication with related link
            self.faculty_members[self.name] = FacultyMember(self.name, self.href, self.publications)  # to create dict

    def fetch_publications(self, link_):
        contents = urllib2.urlopen(link_).read()
        soup = BeautifulSoup(contents, 'html.parser')  # to parse it using BeautifulSoup
        div = soup.find('div', class_="tab-pane active pubs")  # to take div tag which include publications
        publications = [publication.text.encode('utf8').strip().split('\n')[1] for publication in div.find_all('li')]
        return publications  # to return publications and get it in fetch_members method

    def fetch_projects(self, link_):
        contents = urllib2.urlopen(link_).read()  # to open link and read the content
        soup = BeautifulSoup(contents, 'html.parser')  # to parse it using BeautifulSoup
        divs = soup.find_all('div', class_='row')   # to find only div which include row as a class
        for div in divs:
            for project in div.find_all('li'):   # finding li in div part li is each project
                try:   # somethimes it will give a NoneType error
                    title = project.find('a').get('id')   # id in a tag will give us title
                    if title != None:
                        investigator = project.find('a', attrs={'href': re.compile("^/")}).text.encode('utf8').strip()
                        summary = project.find('p', class_='gap').text.encode('utf8').strip()  # to take summary
                        if investigator in self.faculty_members:   # to take only member in self.faculty_members
                            self.projects[title] = ResearchProject(title, summary, investigator)  # add title and obj
                except:
                    pass

    def train_classifier(self):
        for name, member in self.faculty_members.items():
            for publication in member.publications:
                self.classifier.train(publication, name)    # to train classifier obj with each publication

    def predict_pi(self, listbox, name_lbl):  # listbox and name_lbl are widget in the gui class
        selected = listbox.get(listbox.curselection())  # to get selected item
        summary = self.projects[selected].summary   # to find summary of selected item
        predicted_pi = self.classifier.classify(summary)   # to find predicted pi for that summary
        if predicted_pi == self.projects[selected].piname:  # if predicted pi is correct
            name_lbl.config(text=predicted_pi, bg='Green', font=('Arial', 15, 'bold'))  # make label green
        else:
            name_lbl.config(text=predicted_pi, bg='Red', font=('Arial', 15, 'bold'))  # make label red


class GUI(Frame):
    """ GUI class for GUI"""

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.predictor_obj = Predictor()  # predictor class obj
        self.initUI()

    def initUI(self):
        self.pack(fill=BOTH, expand=True)
        Grid.columnconfigure(self, 0, weight=1)
        Label(self, text="PI Estimator Tool for SEHIR CS Projects", bg='blue', fg='white', font=(
            'Arial', 15, 'bold')).grid(sticky=W + E, columnspan=3)  # header
        self.urlentry1 = Entry(self, width=100, justify='center')  # 1st url entry
        self.urlentry1.grid(row=1, pady=20, columnspan=3)
        self.urlentry2 = Entry(self, width=100, justify='center')  # 2nd url entry
        self.urlentry2.grid(row=2, columnspan=3)
        self.fetchbtn = Button(self, text='Fetch', width=15, height=2, command=self.fetch_insert)  # fetch button
        self.fetchbtn.grid(row=3, pady=20, columnspan=3)
        Label(self, text="Projects", font=('Arial', 15, 'bold')).grid(row=4, column=1)  # projects label
        Label(self, text="Prediction", font=('Arial', 15, 'bold')).grid(row=4, column=2, padx=(0, 120))  # predict. label
        self.listbox = Listbox(self, width=100, height=10)
        self.listbox.bind('<<ListboxSelect>>', self.dynamic)
        self.scrollbar = Scrollbar(self, orient='vertical')
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.grid(row=5, column=0, columnspan=2)
        self.scrollbar.grid(row=5, column=1, sticky=N + S + W, padx=(700, 82))
        self.urlentry1.insert(0, 'http://cs.sehir.edu.tr/en/people/')
        self.urlentry2.insert(0, 'http://cs.sehir.edu.tr/en/research/')
        self.label_bool = False  # label bool to create only one label

    def dynamic(self, event):
        if not self.label_bool:  # to check label is exists or not
            self.name_lbl = Label(self, width=15)
            self.name_lbl.grid(row=5, column=2, padx=(0, 50))
            self.label_bool = True
        self.predictor_obj.predict_pi(self.listbox, self.name_lbl)  # to call predict_pi in predictor class

    def fetch_insert(self):  # to fetch all data and insert them in a listbox
        self.predictor_obj.fetch_members(self.urlentry1.get())   # to fetch members
        self.predictor_obj.fetch_projects(self.urlentry2.get())  # to fetch projects
        for project in sorted(self.predictor_obj.projects):   # to insert them in a listbox as sorted
            self.listbox.insert(END, project)
        self.predictor_obj.train_classifier()  # to start train classifier


def main():
    window = Tk()
    window.geometry("1024x450")
    window.title("PI Estimator Tool for SEHIR CS Projects")
    app = GUI(window)
    window.mainloop()


main()
