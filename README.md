# ITDS346_News
## วิธีการรันโค้ด
### การลงเบื้องต้น
- clone github ลงบนเครื่อง
- ลง requirements.txt หรือ library ที่เกี่ยวข้อง

### การทดลองบันทึกข้อมูลข่าว
- ให้ทำการรัน main.py ของทั้ง 3 folder แหล่งข่าว
- จากนั้นจะมี folder output ออกมาซึ่งประกอบไปด้วยไฟล์สำหรับเช็คการดาวน์โหลดและ folder ข่าวของแต่ละสำนักพิมพ์
- ภายใน folder output ของแต่ละสำนักพิมพ์จะประกอบไปด้วย sub folder แบ่งตามวันที่และภายในจะมี folder ข่าวชื่อตาม meta data ของข่าว ประกอบไปด้วย text และ html ไฟล์

### การทดลองประเมิณข้อมูล
- ให้ทำการรัน similarity_evaluation.py โดยเปลี่ยนชื่อ folder ตาม sample ของแหล่งข่าวที่ต้องการทดสอบ
