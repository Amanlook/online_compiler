package main

import (
	"fmt"
	"time"
)

func task(id int) {
	fmt.Printf("Task %d starting\n", id)
	time.Sleep(time.Second) // Simulate some work
	fmt.Printf("Task %d done\n", id)
}

func main() {
	for i := 0; i < 3; i++ {
		go task(i)
	}
	time.Sleep(2 * time.Second) // Allow goroutines to finish
	fmt.Println("Main function done")
}