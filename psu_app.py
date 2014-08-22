__author__ = 'zwhitman'
__author__ = 'sflecher'
__author__ = 'jlam'

import Tkinter as tk
import tkFileDialog as fd
import arcpy
import uuid
import re
import os
import ctypes
import tkMessageBox
import shutil

# Add us_counties and join

TITLE_FONT = ("Helvetica", 18, "bold")

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        SampleApp.wm_title(self, "PSU Creator")
        SampleApp.iconbitmap(self,
                             bitmap="C:\\Users\\zwhitman\\Documents\\census\\psu_app_clean2\\favicon.ico")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageState, PageTwo, PageWarning, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, c):
        '''Show a frame for the given class'''
        frame = self.frames[c]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome to the PSU Creator", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        welcome = tk.Label(self,
                           text="This application is designed to help you create the \n"
                                " best PSUs in the galaxy.\n\n "
                                "Before we begin, we need to set a few things up.",
                           font=("Helvetica", 16))
        welcome.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Start", height=2, width=10, font="Helvetica",
                            command=lambda: controller.show_frame(PageOne))
        #button1.place(relx=.867, rely=.892)
        button1.pack(side="bottom", pady=40)


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.columnconfigure(self, 1, weight=3)
        tk.Frame.columnconfigure(self, 2, weight=3)
        tk.Frame.columnconfigure(self, 3, weight=3)
        label = tk.Label(self, text="Where would you like to save everything?", font=TITLE_FONT)
        label.grid(column=1, row=1, columnspan=5, pady=[10, 0], sticky="nsew")


        def find_loc_directory():
            global path_directory
            path_directory = fd.askdirectory()
            global foldername
            global inputpath
            global outputpath
            global tmppath
            foldername = path_directory.rsplit('\\', 1)[0]
            inputpath = str(foldername+'/input/')
            outputpath = str(foldername+'/output/')
            tmppath = str(foldername+'/tmp/')
            if len(path_directory) <= 54:
                mlabel['text'] = path_directory
            else:
                mlabel['text'] = "..."+path_directory[-54:]
            if mlabel['text'] == path_directory or mlabel['text'] == "..."+path_directory[-54:]:
                try:
                    if flabel['text'] == variable_file or flabel['text'] == "..."+variable_file[-54:]:
                        button2['state'] = 'normal'
                except NameError:
                    button2['state'] = 'disabled'
            return

        def filepath():
            global variable_file
            variable_file = fd.askopenfilename()
            if len(variable_file) <= 54:
                flabel['text'] = variable_file
            else:
                flabel['text'] = "..."+variable_file[-54:]
            if mlabel['text'] == path_directory or mlabel['text'] == "..."+path_directory[-54:]:
                try:
                    if flabel['text'] == variable_file or flabel['text'] == "..."+variable_file[-54:]:
                        button2['state'] = 'normal'
                except NameError:
                    button2['state'] = 'disabled'
            return

        def mhello():
            foldername = path_directory.rsplit('\\', 1)[0]
            arcpy.CreateFolder_management(foldername, 'input')
            arcpy.CreateFolder_management(foldername, 'output')
            arcpy.CreateFolder_management(foldername, 'tmp')
            inputpath = str(foldername+'/input/')
            start_county_layer = "C:\Users\zwhitman\Documents\census\psu_app\input\us_counties.shp"
            global input_county
            input_county = inputpath+'us_counties_joined_3857.shp'
            if os.path.isfile(input_county):
                controller.show_frame(PageState)
            else:
                arcpy.Copy_management(start_county_layer, input_county)
                arcpy.TableToDBASE_conversion(variable_file, inputpath)
                dbf_varfile = variable_file.rsplit('/', 1)[1]
                dbf_varfile = dbf_varfile[:-3]+"dbf"
                dbf_varfile = inputpath+dbf_varfile
                arcpy.AddField_management(dbf_varfile, "GEOID_2", "TEXT", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
                arcpy.CalculateField_management(dbf_varfile, "GEOID_2", "calc(!GEOID!)", "PYTHON_9.3", "def calc(a):\\n     x = a[1:-1] \\n     return x\\n")
                arcpy.JoinField_management(input_county, "GEOID", dbf_varfile, "GEOID_2", "#")
                controller.show_frame(PageState)

            return


        buttonFileBrowse = tk.Button(self, text="Folder Path", height=2, font="Helvetica",
                                     command=lambda: find_loc_directory())


        button = tk.Button(self, text="Go back", font="Helvetica", height=2,
                           command=lambda: controller.show_frame(StartPage))
        button2 = tk.Button(self, text="Continue", state='disabled', font="Helvetica", height=2,
                            command=lambda: mhello())

        buttonFileBrowse.grid(column=1, row=2, pady=10, padx=(20, 10), sticky="nsew")
        button.place(relx=0, rely=1, anchor='sw')
        button2.place(relx=1, rely=1, anchor='se')


        mlabel = tk.Label(self, text="Browse to the folder where you'd like everything to be saved.", font="Helvetica")
        flabel = tk.Label(self, text="Browse to the variable excel spreadsheet to be used to create PSUs.", font="Helvetica")
        filebutton = tk.Button(self, text="Variable File", height=2, font="Helvetica", command=lambda: filepath())
        #mbutton = tk.Button(self, text="Ok", height=2, width=30, font="Helvetica", command=mhello)

        filebutton.grid(column=1, row=3, pady=10, padx=(20, 10), sticky="nsew")
        mlabel.grid(column=2, row=2, columnspan=3, sticky='w')
        flabel.grid(column=2, row=3, columnspan=3, sticky='w')
        #mbutton.grid(column=1, row=4, columnspan=5, sticky="nsew", padx=180, pady=20)


class PageState(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="What state would you like to work on?", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        # Select a specific state
        def select():
            global mxd
            mxd = arcpy.mapping.MapDocument(r"CURRENT")
            global df
            df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
            for x in arcpy.mapping.ListLayers(mxd, "", df):
                arcpy.mapping.RemoveLayer(df, x)
            items = map(int, listbox.curselection())
            itemchoice = items[0]
            global statename
            statename = statelist[itemchoice]
            # create state temp folder
            global tmp_state_folder
            tmp_state_folder = statename+"_"+re.sub('-', '_', str(uuid.uuid4()))
            global fullpath_tmp_state_folder
            fullpath_tmp_state_folder = tmppath+tmp_state_folder+"/"
            arcpy.CreateFolder_management(tmppath, tmp_state_folder)
            statechoice = str(statefips[itemchoice])
            state_select = "STATEFP = '"+statechoice+"'"
            global name1
            name1 = statelist[itemchoice]+"_"+re.sub('-', '_', str(uuid.uuid4()))
            global name3
            name3 = fullpath_tmp_state_folder+name1+".shp"
            name2 = "us_counties_joined_3857"
            arcpy.Select_analysis(input_county, name3, state_select)
            global layer1
            layer1 = arcpy.mapping.ListLayers(mxd, "", df)[0].name
            lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
            df.extent = lyr.getExtent()
            #countylyr = arcpy.mapping.ListLayers(mxd, "", df)[1]
            #arcpy.mapping.RemoveLayer(df, countylyr)
            #Add and calculate population & weighted income
            arcpy.AddField_management(layer1, "POPULATION", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer1, "POPULATION", "!POP!*!ALANDSQM!", "PYTHON")
            arcpy.AddField_management(layer1, "WTDINCOME", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer1, "WTDINCOME", "!INCOME!*!POP!", "PYTHON")

            #Apply natural breaks from pre-defined symbologyLayer
            # symbologyLayer_2 = "C:\Users\zwhitman\Documents\census\psu_app_clean2\inputs\NaturalBreaksSym_2.lyr"
            # arcpy.ApplySymbologyFromLayer_management(layer1, symbologyLayer_2)

            #Apply natural breaks from pre-defined symbologyLayer
            symbologyLayer = "C:\\Users\\zwhitman\\Documents\\census\\psu_app_clean2\\inputs\\NaturalBreaksSym.lyr"
            arcpy.ApplySymbologyFromLayer_management(layer1, symbologyLayer)

            #Create variables from break points
            global breakpt1pop
            global breakpt2pop
            global breakpt3pop
            breakpt1pop = lyr.symbology.classBreakValues[0]
            breakpt2pop = lyr.symbology.classBreakValues[1]
            breakpt3pop = lyr.symbology.classBreakValues[2]


            #Add pop rank field and calculate based on break points
            arcpy.AddField_management(lyr, "POPRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")

            calcstate1 = str("def calc(pop):\\n if pop >= %f:\\n  return 'A'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'C'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "POPRANK", "calc(!POP!)", "PYTHON", calcstate1 % (breakpt3pop, breakpt2pop, breakpt1pop))

            #Apply natural breaks to income layer
            symbologyLayer_2 = "C:\\Users\\zwhitman\\Documents\\census\\psu_app_clean2\\inputs\\NaturalBreaksSym_2.lyr"
            arcpy.ApplySymbologyFromLayer_management(layer1, symbologyLayer_2)
            # lyr.symbology.valueField = "INCOME"
            # lyr.symbology.numClasses = 3

            #Create variables from break points
            global breakpt1inc
            global breakpt2inc
            global breakpt3inc
            breakpt1inc = lyr.symbology.classBreakValues[0]
            breakpt2inc = lyr.symbology.classBreakValues[1]
            breakpt3inc = lyr.symbology.classBreakValues[2]


            #Add income rank field and calculate based on break points
            arcpy.AddField_management(lyr,"INCRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")
            calcstate2 = str("def calc(pop):\\n if pop >= %f:\\n  return 'C'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'A'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "INCRANK", "calc(!INCOME!)", "PYTHON", calcstate2 % (breakpt3inc, breakpt2inc, breakpt1inc))

            #Add combined rank field and calculate concatenation
            arcpy.AddField_management(lyr,"RANK","TEXT","","","2","","NULLABLE","","")
            arcpy.CalculateField_management(lyr,"RANK","!INCRANK! + !POPRANK!","PYTHON")

            #Apply unique symbol symbology from pre-defined symbologyLayer
            RankSymLayer="C:\Users\zwhitman\Documents\census\psu_app\input\RankSymbology.lyr"
            arcpy.ApplySymbologyFromLayer_management(lyr, RankSymLayer)

            # enable continue button
            button2['state'] = 'normal'
            controller.show_frame(PageTwo)



        pagestateframe = tk.Frame(self)
        pagestateframe.pack(side="top", fill="both", padx=5, pady=5)
        scroll = tk.Scrollbar(pagestateframe, bd=0)
        global listbox
        listbox = tk.Listbox(pagestateframe, bd=0, font="Helvetica", yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        listbox.pack(side="top", fill="both")

        scroll.config(command=listbox.yview)
        listbox.config(yscrollcommand=scroll.set)

        statelist = ["Alabama",
                     "Alaska",
                     "Arizona",
                     "Arkansas",
                     "California",
                     "Colorado",
                     "Connecticut",
                     "Delaware",
                     "District of Columbia",
                     "Florida",
                     "Georgia",
                     "Hawaii",
                     "Idaho",
                     "Illinois",
                     "Indiana",
                     "Iowa",
                     "Kansas",
                     "Kentucky",
                     "Louisiana",
                     "Maine",
                     "Maryland",
                     "Massachusetts",
                     "Michigan",
                     "Minnesota",
                     "Mississippi",
                     "Missouri",
                     "Montana",
                     "Nebraska",
                     "Nevada",
                     "New Hampshire",
                     "New Jersey",
                     "New Mexico",
                     "New York",
                     "North Carolina",
                     "North Dakota",
                     "Ohio",
                     "Oklahoma",
                     "Oregon",
                     "Pennsylvania",
                     "Rhode Island",
                     "South Carolina",
                     "South Dakota",
                     "Tennessee",
                     "Texas",
                     "Utah",
                     "Vermont",
                     "Virginia",
                     "Washington",
                     "West Virginia",
                     "Wisconsin",
                     "Wyoming"]

        for item in statelist:
            listbox.insert(tk.END, item)

        global statefips
        statefips = ["01",
                     "02",
                     "04",
                     "05",
                     "06",
                     "08",
                     "09",
                     "10",
                     "11",
                     "12",
                     "13",
                     "15",
                     "16",
                     "17",
                     "18",
                     "19",
                     "20",
                     "21",
                     "22",
                     "23",
                     "24",
                     "25",
                     "26",
                     "27",
                     "28",
                     "29",
                     "30",
                     "31",
                     "32",
                     "33",
                     "34",
                     "35",
                     "36",
                     "37",
                     "38",
                     "39",
                     "40",
                     "41",
                     "42",
                     "44",
                     "45",
                     "46",
                     "47",
                     "48",
                     "49",
                     "50",
                     "51",
                     "53",
                     "54",
                     "55",
                     "56"]


        button = tk.Button(self, text="Go back", font="Helvetica", height=2,
                           command=lambda: controller.show_frame(PageOne))
        button2 = tk.Button(self, text="Continue", state='normal', font="Helvetica", height=2,
                            command=lambda: select())

        #button_choosestate.pack(side="top")
        button.place(relx=0, rely=1, anchor='sw')
        button2.place(relx=1, rely=1, anchor='se')


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Let's Get Down to Business", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button3 = tk.Button(self, text="Continue", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageThree))
        button1 = tk.Button(self, text="Go back", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageWarning))

        dissolve_del_frame = tk.Frame(self)
        dissolve_del_frame.pack(side="top")


        info_button = tk.Button(self, text="Check Stats", font="Helvetica", height=2,
                            command=lambda: info_check())

        info_button.pack(side="top")

        def info_check():
            info_label = arcpy.SearchCursor(name1, fields="Name_1; ALANDSQM; POP; INCOME; POPULATION")
            # for row in info_label:
            #     print("County: {0}, Area: {1}, Pop. Density: {2}, Income: {3}, Population: {4}".format(
            #         row.getValue("Name_1"),
            #         row.getValue("ALANDSQM"),
            #         row.getValue("POP"),
            #         row.getValue("INCOME"),
            #         row.getValue("POPULATION")
            #     ))
            graph = arcpy.Graph()
            graph.addSeriesScatterPlot(name1, fieldY="POP", fieldX="INCOME")
            graph_tee = "C:\\Users\\zwhitman\\Documents\\census\\psu_app_clean2_backup\\inputs\\graph_template.tee"
            arcpy.MakeGraph_management(graph_tee, graph, out_graph_name=name1+".grf")
            # arcpy.MakeGraph_management(arcpy.GraphTemplate(), graph, out_graph_name=name1+".grf")

        def dissolve_button_func():
            desc = arcpy.Describe(layer1)
            save_name = desc.FIDSet
            save_name2 = save_name.replace("; ", "_")
            arcpy.Dissolve_management(layer1, fullpath_tmp_state_folder + "psu_" + save_name2,
                                      "#", "WTDINCOME SUM;POP SUM;ALANDSQM SUM;POPULATION SUM", "MULTI_PART", "DISSOLVE_LINES")
            lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
            layer2 = arcpy.mapping.ListLayers(mxd, "", df)[0].name
            #symbologyLayer = "C:\Users\zwhitman\Documents\census\psu_app\input\NaturalBreaksSym.lyr"

            #Add and calculate population & weighted income
            arcpy.AddField_management(layer2, "NEW_POP", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer2, "NEW_POP", "!SUM_POPULA!/ !SUM_ALANDS!", "PYTHON")
            arcpy.AddField_management(layer2, "INCOME", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer2, "INCOME", "!SUM_WTDINC! / !SUM_POP!", "PYTHON")

            #Add pop rank field and calculate based on break points
            arcpy.AddField_management(lyr, "POPRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")

            calcstate1 = str("def calc(pop):\\n if pop >= %f:\\n  return 'A'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'C'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "POPRANK", "calc(!NEW_POP!)", "PYTHON", calcstate1 % (breakpt3pop, breakpt2pop, breakpt1pop))

            #Add income rank field and calculate based on break points
            arcpy.AddField_management(lyr,"INCRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")
            calcstate2 = str("def calc(pop):\\n if pop >= %f:\\n  return 'C'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'A'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "INCRANK", "calc(!INCOME!)", "PYTHON", calcstate2 % (breakpt3inc, breakpt2inc, breakpt1inc))

            #Add combined rank field and calculate concatenation
            arcpy.AddField_management(lyr,"RANK","TEXT","","","2","","NULLABLE","","")
            arcpy.CalculateField_management(lyr,"RANK","!INCRANK! + !POPRANK!","PYTHON")

            #Apply unique symbol symbology from pre-defined symbologyLayer
            RankSymLayer="C:\Users\zwhitman\Documents\census\psu_app_clean2_backup\inputs\PSUSymbology.lyr"
            arcpy.ApplySymbologyFromLayer_management(lyr, RankSymLayer)

            #Error If Statements
            cursor = arcpy.SearchCursor(lyr)
            MessageBox = ctypes.windll.user32.MessageBoxA
            for row in cursor:
                if row.getValue("SUM_ALANDS")>3000 and row.getValue("SUM_POPULA")<7500:
                    MessageBox(None,'FYI - Your PSU has a population < 7,500 AND sq.mi. > 3,000','Windowtitle',0)
                elif row.getValue("SUM_POPULA")<7500:
                    MessageBox(None,'FYI - Your PSU has a population of less than 7,500','Windowtitle',0)
                elif row.getValue("SUM_ALANDS")>3000:
                    MessageBox(None,'FYI - Your PSU is over 3,000 sq.mi.','Windowtitle',0)

            #Color labels if breaks rules
            expression="""Function FindLabel([SUM_POPULA],[SUM_ALANDS]):\n  if (cLng([SUM_POPULA]) <= 7500 OR cLng([SUM_ALANDS]) >= 3000) then\n   FindLabel= "<CLR red='255'><FNT size = '14'>" + [SUM_ALANDS] + "</FNT></CLR>"\n  else\n   FindLabel = [SUM_ALANDS]\n  end if\nEnd Function"""
            lyr.labelClasses[0].expression=expression
            for lblClass in lyr.labelClasses:
              lblClass.showClassLabels=True
            lyr.showLabels=True
            arcpy.RefreshActiveView()
            global mxd_layerlist
            mxd_layerlist = arcpy.mapping.ListLayers(mxd)
            arcpy.SelectLayerByAttribute_management(layer1, "CLEAR_SELECTION")
            return

        def test_delete():
            global deletion_layer
            deletion_layer = ""
            mxd_layerlist = arcpy.mapping.ListLayers(mxd)
            for layer in mxd_layerlist:
                desc = arcpy.Describe(layer)
                if desc.fidSet:
                    if layer.name[0:3] == "psu":
                        deletion_layer = layer.name
            if deletion_layer[0:3] == "psu":
                arcpy.Delete_management(fullpath_tmp_state_folder+deletion_layer+".shp", "#")
            else:
                arcpy.Delete_management(fullpath_tmp_state_folder+arcpy.mapping.ListLayers(mxd, "psu*", df)[0].name+".shp", "#")

        dissolve_button = tk.Button(dissolve_del_frame, text="Create PSU", font="Helvetica", height=2, width=20,
                                    command=lambda: dissolve_button_func())

        delete_button = tk.Button(dissolve_del_frame, text="Delete PSU", font="Helvetica", height=2, width=20,
                                    command=lambda: test_delete())

        dissolve_button.pack(side="left", anchor="n", pady=15)
        delete_button.pack(side="left", anchor="n", pady=15)

        button1.place(relx=0, rely=1, anchor='sw')
        button3.place(relx=1, rely=1, anchor='se')

class PageWarning(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Warning: This will erase your work.\n\nStill want to go back?", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        yes_no_frame = tk.Frame(self)
        yes_no_frame.pack(side="top", pady=15)
        button3 = tk.Button(yes_no_frame, text="No", font="Helvetica", height=2, width=15,
                            command=lambda: controller.show_frame(PageTwo))
        button1 = tk.Button(yes_no_frame, text="Yes", font="Helvetica", height=2, width=15,
                            command=lambda: backstate())

        def backstate():
            for x in arcpy.mapping.ListLayers(mxd, "", df):
                # arcpy.mapping.RemoveLayer(df, x)
                arcpy.Delete_management(x)
            shutil.rmtree(fullpath_tmp_state_folder)
            controller.show_frame(PageState)
            return

        button1.pack(side="left")
        button3.pack(side="left")


class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Let's Export This Thing", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        def export_button_func():
            #merge PSUs
            arcpy.CreateFolder_management(outputpath, tmp_state_folder)
            arcpy.env.workspace = fullpath_tmp_state_folder
            fcList = arcpy.ListFeatureClasses("*psu*", "polygon", "")
            tem_merge_file_no_shp = "PSUmerge_"+statename+"_"+re.sub('-', '_', str(uuid.uuid4()))
            tem_merge_file = tem_merge_file_no_shp+".shp"
            out_merge_file_no_shp = "allMerge_"+statename+"_"+re.sub('-', '_', str(uuid.uuid4()))
            out_merge_file = out_merge_file_no_shp+".shp"
            arcpy.Merge_management(fcList, tem_merge_file)

            #Select counties that overlap PSUs and inverse selection
            arcpy.SelectLayerByLocation_management(name1, "WITHIN", tem_merge_file_no_shp, "", "NEW_SELECTION")
            arcpy.SelectLayerByLocation_management(name1, "WITHIN", tem_merge_file_no_shp, "", "SWITCH_SELECTION")

            #Merge PSUs with Counties
            state_output_path = outputpath+tmp_state_folder+'/'
            arcpy.Merge_management([name1, tem_merge_file_no_shp], state_output_path+out_merge_file)
            arcpy.SelectLayerByAttribute_management(out_merge_file_no_shp, "NEW_SELECTION", """"POPULATION"=0""")
            arcpy.CalculateField_management(out_merge_file_no_shp, "POPULATION", "!SUM_POPULA!", "PYTHON")
            arcpy.CalculateField_management(out_merge_file_no_shp, "ALANDSQM", "!SUM_ALANDS!", "PYTHON")

            #Exporting shapefile to csv (and ignoring umlaut character)
            u = unichr(253)
            u.encode('ascii', 'ignore')
            import arcgisscripting, csv
            gp=arcgisscripting.create(10.2)
            output=open(r""+state_output_path+"tableOutput"+statename+"_"+re.sub('-', '_', str(uuid.uuid4()))+".csv","w")
            linewriter=csv.writer(output,delimiter=',')
            fcdescribe=gp.Describe(r""+state_output_path+out_merge_file)
            flds=fcdescribe.Fields
            header = []
            for fld in flds:
                value=fld.Name
                header.append(value)
            linewriter.writerow(header)
            cursor = gp.searchcursor(r""+state_output_path+out_merge_file)
            row = cursor.Next()
            while row:
                line=[]
                for fld in flds:
                    value=row.GetValue(fld.Name)
                    line.append(value)
                linewriter.writerow(line)
                del line
                row=cursor.Next()

            #Zoom to state layer extent
            #(statelyr variable set to state layer)
            lyr = arcpy.mapping.ListLayers(mxd, out_merge_file_no_shp, df)[0]

            RankSymLayer="C:\Users\zwhitman\Documents\census\psu_app\input\RankSymbology.lyr"
            arcpy.ApplySymbologyFromLayer_management(lyr, RankSymLayer)

            #Add SQMI and POPULATION labels
            # expression = """"S:" & [SQMI] & vbCrLf& "P:" & [POPULATION]"""
            # lyr.labelClasses[0].expression=expression
            # for lblClass in lyr.labelClasses:
            #   lblClass.showClassLabels=True
            # lyr.showLabels=True
            # arcpy.RefreshActiveView()

            newExtent=df.extent
            statelyr_extent=lyr.getExtent()
            newExtent.XMin=statelyr_extent.XMin
            newExtent.YMin=statelyr_extent.YMin
            newExtent.XMax=statelyr_extent.XMax
            newExtent.YMax=statelyr_extent.YMax
            df.extent=newExtent

            #Clear Selection
            arcpy.SelectLayerByAttribute_management(name1,"CLEAR_SELECTION")

            #Export map to pdf
            arcpy.mapping.ExportToJPEG(mxd, r""+state_output_path+"mapOutput.jpg")

            # do something
            return

        def loopback():
            controller.show_frame(PageState)
            for x in arcpy.mapping.ListLayers(mxd, "", df):
                arcpy.mapping.RemoveLayer(df, x)
            return


        export_button = tk.Button(self, text="Export", font="Helvetica", height=2, width=20,
                                  command=lambda: export_button_func())

        continue_states = tk.Button(self, text="New State", state='normal', font="Helvetica", height=2,
                            command=lambda: loopback())

        export_button.pack(side="top", pady=15)

        button2 = tk.Button(self, text="Go back", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageTwo))

        button2.place(relx=0, rely=1, anchor='sw')
        continue_states.place(relx=1, rely=1, anchor='se')


def handler():
    if os.path.isdir(tmppath) is True:
        delete_message = "Quitting will erase the folder: "+tmppath+".\nAre you sure you want to quit?"
    else:
        delete_message = "Are you sure you want to quit?"
    if tkMessageBox.askokcancel("Quit?", delete_message):
        try:
            tmppath
        except NameError:
            app.destroy()
        else:
            if os.path.isdir(tmppath) is True:
                for x in arcpy.mapping.ListLayers(mxd, "", df):
                    arcpy.Delete_management(x)
                shutil.rmtree(tmppath)
                app.destroy()
            else:
                app.destroy()

if __name__ == "__main__":
    app = SampleApp()
    app.minsize(width=650, height=300)
    app.wm_attributes("-topmost", 1)
    app.protocol("WM_DELETE_WINDOW", handler)
    app.mainloop()
