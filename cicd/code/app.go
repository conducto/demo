package main

import (
  "fmt"
  "os"
  "time"
)

// Simple program that prints message.
// --test argument invokes pretend tests, that will always pass.
func main() {
  if len(os.Args) < 2 {
    fmt.Println("This is my app binary")
  } else {
    if os.Args[1] == "--test" {
      fmt.Println("Pretending to run app tests...")
      for i := 0; i < 8; i++ {
        time.Sleep(time.Second)
        fmt.Fprintln(os.Stderr, "test", i, "[OK]")
      }
      fmt.Println("All tests pass!")
    }
  }
}
