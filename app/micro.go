package main

import (
	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var db *gorm.DB

type User struct {
	gorm.Model
	Name     string  `gorm:"uniqueIndex;not null"`
	Password string  `gorm:"not null"`
	Age      int     `gorm:"not null"`
	Balance  float64 `gorm:"default:0"`
}

type Item struct {
	gorm.Model
	Name         string  `gorm:"not null"`
	SalesmanName string  `gorm:"not null"`
	Price        float64 `gorm:"not null"`
	Category     string  `gorm:"not null"`
}

type Order struct {
	gorm.Model
	UserName     string  `gorm:"not null"`
	Quantity     int     `gorm:"not null"`
	SalesmanName string  `gorm:"not null"`
	Price        float64 `gorm:"not null"`
	TotalPrice   float64 `gorm:"not null"`
}

func GetAllItems() ([]Item, error) {
	var items []Item
	result := db.Find(&items)
	return items, result.Error
}

func GetItemsByCategory(category string) ([]Item, error) {
	var items []Item
	result := db.Where("category = ?", category).Find(&items)
	return items, result.Error
}

func CreateOrder(userName string, quantity int, salesmanName string, price float64) (Order, error) {
	order := Order{
		UserName:     userName,
		Quantity:     quantity,
		SalesmanName: salesmanName,
		Price:        price,
		TotalPrice:   float64(quantity) * price,
	}
	result := db.Create(&order)
	return order, result.Error
}

func GetUserByName(name string) (User, error) {
	var user User
	result := db.Where("name = ?", name).First(&user)
	return user, result.Error
}

func main() {
	var err error
	db, err = gorm.Open(sqlite.Open("marketplace.db"), &gorm.Config{})
	if err != nil {
		panic("Нет базы")
	}
	db.AutoMigrate(&User{}, &Item{}, &Order{})

	r := gin.Default()

	// Товары
	r.GET("/items", func(c *gin.Context) {
		items, err := GetAllItems()
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, items)
	})

	// Товары по категории
	r.GET("/items/:category", func(c *gin.Context) {
		category := c.Param("category")
		items, err := GetItemsByCategory(category)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, items)
	})

	// Создать заказ
	r.POST("/orders", func(c *gin.Context) {
		var req struct {
			UserName     string  `json:"user_name"`
			Quantity     int     `json:"quantity"`
			SalesmanName string  `json:"salesman_name"`
			Price        float64 `json:"price"`
		}
		c.ShouldBindJSON(&req)
		order, err := CreateOrder(req.UserName, req.Quantity, req.SalesmanName, req.Price)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(201, order)
	})

	// Проверить пользователя (для Python)
	r.GET("/users/:name", func(c *gin.Context) {
		name := c.Param("name")
		user, err := GetUserByName(name)
		if err != nil {
			c.JSON(404, gin.H{"error": "Не найден"})
			return
		}
		c.JSON(200, user)
	})

	r.Run(":3333")
}
