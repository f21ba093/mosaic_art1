from PIL import Image,ImageFilter
import subprocess
import os
import random
import math
import time
import cv2 as cv
import numpy as np

#==============設定===================
#素材画像の入っているフォルダ
SourceDir=os.getcwd()+"/source/"

#目標となる画像
GoalImage=os.getcwd()+"muscledog.jpg"

#出力の名前
OutputImage="output.jpg"

#動画
OutputMovie="movie.mp4"

#動画のフレームレート
Framerate=25

#動画フォーマット
fourcc="mp4v"

#フレームスキップ
FrameSkip=30

#素材画像の色の平均値を出す時に色を取得する間隔
PickInterval=(1,1)

#素材の画像のサイズ(読み込み時にここで指定したサイズに変換される)
SourceImageSize=(100,100)

#x,yそれぞれ何個の画像を並べるか
TileCount=(100,100)

#ターゲット画像の倍率
TargetZoom=5
#=====================================


def ColorAvg(img,interval=(1,1)): #pythonのループ使用
	#画像の色の平均値を求める
	s=(0,0,0)
	n=0
	for y in range(0,img.size[1],interval[1]):
		for x in range(0,img.size[0],interval[0]):
			c=img.getpixel((x,y))
			s=tuple(i+k for i,k in zip(s,c))
			n=n+1
	s=tuple(math.floor(i/n) for i in s)
	return s

def ColorChange(img,col,Avg):
	#imgの色の平均値がcolになるようにフィルターに掛ける
	#元画像の平均値を必要とする
	ds=tuple(i-k for i,k in zip(col,Avg))
	r,g,b=img.split()[0:3]
	r=r.point(lambda x: x+ds[0] if 0 <= x+ds[0] and x+ds[0] < 256 else 0 if x+ds[0] < 0 else 255)
	g=g.point(lambda x: x+ds[1] if 0 <= x+ds[1] and x+ds[1] < 256 else 0 if x+ds[1] < 0 else 255)
	b=b.point(lambda x: x+ds[2] if 0 <= x+ds[2] and x+ds[2] < 256 else 0 if x+ds[2] < 0 else 255)
	return Image.merge("RGB",(r,g,b))

def Mosaic(img,src,video=None,count=(100,100),interval=(10,10),FrameSkip=0):
	#モザイクアートを生成する
	#img:元画像
	#dst:動画の保存先
	#src:モザイクアートに使う画像群
	#count:x方向,y方向にそれぞれ何個の画像を使うか
	#split:画像の色平均を取る時に色を取得する間隔
	
	Target=Image.new("RGB",img.size)
	print("%s:各素材グラフィックの色平均値を導出開始"%(str(time.time()-startTime)))
	SourceImg=[(i,ColorAvg(i,interval)) for i in src]
	SourceImgTemp=[]
	print("%s:各素材グラフィックの色平均値を導出完了"%(str(time.time()-startTime)))
	print("%s:タイルリストを生成開始"%(str(time.time()-startTime)))
	RectList=[]
	for y in range(0,count[1]):
		for x in range(0,count[0]):
			tileRect=(x*img.size[0]/count[0],y*img.size[1]/count[1],(x+1)*img.size[0]/count[0],(y+1)*img.size[1]/count[1])
			tileRect=tuple(math.floor(i) for i in tileRect)
			RectList.append(tileRect)
	print("%s:タイルリストを生成完了"%(str(time.time()-startTime)))
	print("%s:モザイクアートを生成開始"%(time.time()-startTime))
	TileCount=0
	Frame=np.array(Target)[:,:,::-1]
	video.write(Frame)
	while(len(RectList)>0):
		r=random.randrange(len(RectList))
		tileRect=RectList[r]
		del RectList[r]
		Pivot=img.getpixel((math.floor((tileRect[0]+tileRect[2])/2),math.floor((tileRect[1]+tileRect[3])/2)))
		if(len(SourceImgTemp)==0):
			SourceImgTemp=SourceImg.copy()
		r=random.randrange(len(SourceImgTemp))
		tempSrc=ColorChange(SourceImgTemp[r][0],Pivot,SourceImgTemp[r][1])
		del SourceImgTemp[r]
		tempSrc=tempSrc.resize((tileRect[2]-tileRect[0],tileRect[3]-tileRect[1]))
		Target.paste(tempSrc,(tileRect[0],tileRect[1]))
		if(TileCount%(FrameSkip+1)==0 and type(video)==cv.VideoWriter):
			Frame=np.array(Target)[:,:,::-1]
			video.write(Frame)
			#cv.imshow("",Frame)
			#cv.waitKey(1)
		TileCount+=1
	Frame=np.array(Target)[:,:,::-1]
	video.write(Frame)
	print("%s:モザイクアートを生成完了"%(str(time.time()-startTime)))
	return Target

if __name__=="__main__":
	startTime=time.time()
	Res=subprocess.run(["ls",SourceDir],stdout=subprocess.PIPE)
	Res=Res.stdout.decode().split("\n")
	Res=Res[:len(Res)-1]
	src=[Image.open(SourceDir+i).resize(SourceImageSize) for i in Res]
	target=Image.open(GoalImage)
	target=target.resize(tuple(math.floor(i*TargetZoom) for i in target.size))
	fourcc2=cv.VideoWriter.fourcc(*fourcc)
	v=cv.VideoWriter(OutputMovie,int(fourcc2),Framerate,target.size)
	Mosaic(target,src,video=v,interval=PickInterval,count=TileCount,FrameSkip=FrameSkip).save(OutputImage)
	v.release()
