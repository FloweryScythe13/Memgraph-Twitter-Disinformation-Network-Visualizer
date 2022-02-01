from dataclasses import dataclass
import json as js
from enum import Enum


class Parameter(Enum):
    ID = "id"
    LABELS = "labels"
    PROPERTIES = "properties"
    TYPE = "type"
    END = "end"
    LABEL = "label"
    START = "start"
    NODE = "node"
    RELATIONSHIP = "relationship"


@dataclass
class Node:
    id: int
    labels: list
    properties: dict
    
    @classmethod
    def from_vertex(cls, vertex):
        return cls(vertex.id, vertex.labels, vertex.properties)

    def get_dict(self) -> dict:
        return {
            Parameter.ID.value: self.id,
            Parameter.LABELS.value: self.labels,
            Parameter.PROPERTIES.value: self.properties,
            Parameter.TYPE.value: Parameter.NODE.value,
        }


@dataclass
class Relationship:
    end: int
    id: int
    label: str
    properties: dict
    start: int

    def get_dict(self) -> dict:
        return {
            Parameter.END.value: self.end,
            Parameter.ID.value: self.id,
            Parameter.LABEL.value: self.label,
            Parameter.PROPERTIES.value: self.properties,
            Parameter.START.value: self.start,
            Parameter.TYPE.value: Parameter.RELATIONSHIP.value,
        }
        
