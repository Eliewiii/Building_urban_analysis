# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 15:30:50 2018

@author: medionie
"""
import os
def fc_calcul_Radiance(rfluxmtx,Fichier_emetteur,Fichier_recepteur,output,Fichier_scene,path_radiance,path_file_point_oct,path_file_point_rad):
    os.system('CD /D '+ path_radiance +" & "+rfluxmtx+" -h- -ab 0 -c 100000 "+ '"!xform -I '+path_file_point_rad+Fichier_emetteur+'" '+path_file_point_rad+Fichier_recepteur+' -i '+path_file_point_oct+Fichier_scene+">"+output)
    print('CD /D '+ path_radiance +" & "+rfluxmtx+" -h- -ab 0 -c 100000 "+ '"!xform -I '+path_file_point_rad+Fichier_emetteur+'" '+path_file_point_rad+Fichier_recepteur+' -i '+path_file_point_oct+Fichier_scene+">"+output)

def fc_calcul_Radiance_multiple(rfluxmtx,surface_emettrice,list_surface_receptrice,Fichier_scene,path_radiance,path_file_point_oct,path_file_point_rad_emetteur,path_file_point_rad_recepteur,path_file_point_FF):
    commande='CD /D '+ path_radiance
    for i in range(int(len(list_surface_receptrice)//10)):
        for j in range(10):
            commande=commande+" & "+rfluxmtx+" -h- -ab 0 -c 10000 "+ '"!xform -I '+path_file_point_rad_emetteur+surface_emettrice+'.rad'+'" '+path_file_point_rad_recepteur+list_surface_receptrice[10*i+j]+'.rad'+' -i '+path_file_point_oct+Fichier_scene+">"+path_file_point_FF+surface_emettrice+'_'+list_surface_receptrice[10*i+j]+'.txt'
        os.system(commande)
        commande=commande='CD /D '+ path_radiance
    for j in range(int(len(list_surface_receptrice)%10)):
        commande=commande+" & "+rfluxmtx+" -h- -ab 0 -c 10000 "+ '"!xform -I '+path_file_point_rad_emetteur+surface_emettrice+'.rad'+'" '+path_file_point_rad_recepteur+list_surface_receptrice[-j-1]+'.rad'+' -i '+path_file_point_oct+Fichier_scene+">"+path_file_point_FF+surface_emettrice+'_'+list_surface_receptrice[-j-1]+'.txt'
    os.system(commande)

def fc_calcul_Radiance_grouped(rfluxmtx,surface_emettrice,Fichier_scene_point_rad,path_radiance,path_file_point_oct,path_file_point_rad_emetteur,path_file_point_FF):
    # on a touts les surfaces dans un point.rad, il calculs plusieurs FF a la fois
    commande='CD /D '+ path_radiance+" & "+rfluxmtx+" -h- -ab 0 -c 100000 "+ '"!xform -I '+path_file_point_rad_emetteur+surface_emettrice+'.rad'+'" '+path_file_point_oct+Fichier_scene_point_rad+'.rad'+">"+path_file_point_FF+surface_emettrice+'.txt'
    print(commande)
    os.system(commande)

def fc_calcul_Radiance_grouped_splited(rfluxmtx,surface_emettrice,list_Fichier_recepteur_point_rad,Fichier_scene,path_radiance,path_file_point_oct,path_file_point_rad_emetteur,path_file_point_rad_recepteur,path_file_point_FF):
    # on a touts les surfaces dans un point.rad, il calculs plusieurs FF a la fois
    FF=''
    for i in range (len(list_Fichier_recepteur_point_rad)):
        commande='CD /D '+ path_radiance+" & "+rfluxmtx+" -h- -ab 0 -c 10000 "+ '"!xform -I '+path_file_point_rad_emetteur+surface_emettrice+'.rad'+'" '+path_file_point_rad_recepteur+list_Fichier_recepteur_point_rad[i]+'.rad'+' -i '+path_file_point_oct+Fichier_scene+'.oct '+"> "+path_file_point_FF+surface_emettrice+'.txt'
        os.system(commande)
        with open(path_file_point_FF+surface_emettrice+'.txt','r') as file_FF :
            data=file_FF.read().split('\t')
            for j in range(len(data)//3):
                FF+=data[3*j]+' '
    with open(path_file_point_FF+surface_emettrice+'.txt','w') as file_FF :
        file_FF.write(FF[:-1])
