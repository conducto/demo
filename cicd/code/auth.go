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
    fmt.Println("This is my auth binary")
  } else {
    if os.Args[1] == "--test" {
      fmt.Println("Pretending to run auth tests...")
      for i := 0; i < 5; i++ {
        time.Sleep(time.Second)
        fmt.Fprintln(os.Stderr, "test", i, "[OK]")
      }
      fmt.Println("All tests pass!")
    }
  }
}
