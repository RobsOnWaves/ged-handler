import React from 'react';
import Tree from 'react-d3-tree';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';


const orientation = 'vertical';

const translate = {
  x: 0,
  y: 50
};


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
      ]
    },
  ],
};

export default function OrgChartTree() {

  return (
    <Container fluid>
      <Row className="justify-content-center mt-5" >
        <Col md={6}>
          <div id="treeWrapper" style={ { height: 100 } }>
            <Tree data={OrgChart} orientation={orientation} translate={translate} />
          </div>
        </Col>
      </Row>
    </Container>
  );
}