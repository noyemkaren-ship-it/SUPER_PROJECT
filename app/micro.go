// micro.go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var db *gorm.DB

type Item struct {
	gorm.Model
	Name         string  `gorm:"not null"`
	SalesmanName string  `gorm:"not null"`
	Price        float64 `gorm:"not null"`
	Category     string  `gorm:"not null"`
}

func main() {
	var err error
	db, err = gorm.Open(sqlite.Open("app.db"), &gorm.Config{})
	if err != nil {
		panic("Нет базы")
	}
	db.AutoMigrate(&Item{})

	// Добавим тестовые товары, если таблица пустая
	var count int64
	db.Model(&Item{}).Count(&count)
	if count == 0 {
		db.Create(&Item{Name: "Макбук Pro", SalesmanName: "Тигр", Price: 50000, Category: "Электроника"})
		db.Create(&Item{Name: "Acer Aspire", SalesmanName: "Тигр", Price: 7000, Category: "Ноутбуки"})
		db.Create(&Item{Name: "Кофе 3 в 1", SalesmanName: "Сэнсэй", Price: 30, Category: "Напитки"})
	}

	r := gin.Default()

	r.GET("/items", func(c *gin.Context) {
		var items []Item
		db.Find(&items)
		c.JSON(http.StatusOK, items)
	})

	r.GET("/items/:category", func(c *gin.Context) {
		category := c.Param("category")
		var items []Item
		db.Where("category = ?", category).Find(&items)
		c.JSON(http.StatusOK, items)
	})

	r.POST("/orders", func(c *gin.Context) {
		var req struct {
			UserName     string  `json:"user_name"`
			Quantity     int     `json:"quantity"`
			SalesmanName string  `json:"salesman_name"`
			Price        float64 `json:"price"`
		}
		c.ShouldBindJSON(&req)
		c.JSON(http.StatusCreated, gin.H{
			"id":            1,
			"user_name":     req.UserName,
			"quantity":      req.Quantity,
			"salesman_name": req.SalesmanName,
			"price":         req.Price,
			"total_price":   float64(req.Quantity) * req.Price,
		})
	})

	r.Run(":3333")
}
