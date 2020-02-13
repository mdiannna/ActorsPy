defmodule StarterProjectTest do
  use ExUnit.Case
  doctest StarterProject

  test "greets the world" do
    assert StarterProject.hello() == :world
  end
end
