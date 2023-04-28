import React from 'react';
import Tree from 'react-d3-tree';

// This is a simplified example of an org chart with a depth of 2.
// Note how deeper levels are defined recursively via the `children` property.
const OrgChart = {

    "name": {
        "given_names": ["kookoo"],
        "family_name": "coconut"
    },
    "children": [
        {
            "name": {
                "given_names": ["Tristan", "ducoin"],
                "family_name": "Le Breton"
            },
            "children": [],
            "attributes": {
                "sex": "male",
                "birth": {
                    "date_info": {
                        "date": "1950-03-07",
                        "date_type": "full_date"
                    },
                    "place": "TUNIS,Tunisie"
                },
                "death": {
                    "date_info": {
                        "date": "2019-02-12",
                        "date_type": "full_date"
                    },
                    "place": "Toulouse,France"
                }
            }
        }
    ],
    "attributes": {
        "sex": "male",
        "birth": {
            "date_info": {
                "date": "1950-06-06",
                "date_type": "full_date"
            },
            "place": "FORCALQUIER,France"
        }
    }


};

export default function OrgChartTree() {
    return (
        // `<Tree />` will fill width/height of its container; in this case `#treeWrapper`.
        <div id="treeWrapper" style={{ width: '50em', height: '20em' }}>
            <Tree data={OrgChart} />
        </div>
    );
}