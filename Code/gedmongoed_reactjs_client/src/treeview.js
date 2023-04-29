import React from 'react';
import Tree from 'react-d3-tree';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';


// This is a simplified example of an org chart with a depth of 2.
// Note how deeper levels are defined recursively via the `children` property.
const OrgChart = {

    name: 'CEO',
  children: [
    {
      name: 'Manager',
      attributes: {
        department: 'Production',
      },
      children: [
        {
          name: 'Foreman',
          attributes: {
            department: 'Fabrication',
          },
          children: [
            {
              name: 'Worker',
            },
          ],
        },
        {
          name: 'Foreman',
          attributes: {
            department: 'Assembly',
          },
          children: [
            {
              name: 'Worker',
            },
          ],
        },
      ],
    },
  ],
};

export default function OrgChartTree() {
    return (
        <Container>
            <Row className="justify-content-center mt-5">
                <Col md={6}>
                    {// `<Tree />` will fill width/height of its container; in this case `#treeWrapper`.
                    }
                    <div id="treeWrapper" style={{ width: '100em', height: '50em' }}>
                        <Tree data={OrgChart} />
                    </div>
                </Col>
            </Row>
        </Container>
    );
}