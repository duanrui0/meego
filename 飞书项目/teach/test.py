import turtle

# 创建一个绘画窗口
window = turtle.Screen()
window.bgcolor("black")

# 创建一个海龟对象
ironman = turtle.Turtle()
ironman.speed(2)  # 设置绘制速度

# 绘制身体
ironman.color("red")
ironman.begin_fill()
ironman.circle(50)
ironman.end_fill()

# 绘制头部
ironman.penup()
ironman.goto(0, 100)
ironman.pendown()
ironman.color("gold")
ironman.begin_fill()
ironman.circle(30)
ironman.end_fill()

# 绘制眼睛
ironman.penup()
ironman.goto(-15, 110)
ironman.pendown()
ironman.color("white")
ironman.begin_fill()
ironman.circle(10)
ironman.end_fill()

ironman.penup()
ironman.goto(15, 110)
ironman.pendown()
ironman.color("white")
ironman.begin_fill()
ironman.circle(10)
ironman.end_fill()

# 绘制嘴巴
ironman.penup()
ironman.goto(-25, 85)
ironman.pendown()
ironman.width(5)
ironman.goto(25, 85)

# 绘制胸部反应器
ironman.penup()
ironman.goto(-30, 50)
ironman.pendown()
ironman.color("blue")
ironman.begin_fill()
for _ in range(2):
    ironman.forward(60)
    ironman.circle(15, 180)
ironman.end_fill()

# 隐藏海龟箭头
ironman.hideturtle()

# 结束绘制
turtle.done()
